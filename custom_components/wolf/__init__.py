import asyncio
import logging
import re
from dataclasses import dataclass
from socket import AF_INET

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PORT
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from wolf_ism8 import Ism8

from .const import CONF_FW_VERSION
from .const import DOMAIN
from .const import WOLF
from .const import WOLF_ISM8

_LOGGER = logging.getLogger(__name__)


@dataclass
class WolfData:
    """Data for the Wolf integration."""

    protocol: Ism8
    server: asyncio.Server
    fw_version: str = "1.00"


PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
]


def _add_devices(registry: dr.DeviceRegistry, entry: ConfigEntry[WolfData]) -> None:
    """Create the ISM8 adapter device and each selected child device."""
    parent_device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="ISM8 Adapter",
        manufacturer=WOLF,
        model=WOLF_ISM8,
    )

    for device_name in entry.data[CONF_DEVICES]:
        registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device_name)},
            name=device_name,
            via_device_id=parent_device.id,
        )


def _remove_devices(registry: dr.DeviceRegistry, entry: ConfigEntry[WolfData]) -> None:
    """Remove devices a reconfigure deselected, so their entities don't linger.
    The adapter is identified by the entry id and stays.
    """
    keep = {entry.entry_id, *entry.data[CONF_DEVICES]}
    for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
        # identifiers this integration registered under its own domain
        owned = {
            identifier for domain, identifier in device.identifiers if domain == DOMAIN
        }
        if not owned or owned & keep:
            continue
        _LOGGER.debug("removing deselected device %s", device.name)
        registry.async_remove_device(device.id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry[WolfData]) -> bool:
    """set up the integration"""
    ism8 = Ism8()

    server = await hass.loop.create_server(
        ism8.factory,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        family=AF_INET,
    )

    entry.runtime_data = WolfData(
        protocol=ism8,
        server=server,
        fw_version=entry.data.get(CONF_FW_VERSION) or "1.00",
    )

    registry = dr.async_get(hass)
    _add_devices(registry, entry)
    _remove_devices(registry, entry)

    @callback
    def on_connection(ip_address: str) -> None:
        """Handle connection to ISM8."""
        _LOGGER.debug("ISM8 connection to %s, starting info scraping", ip_address)
        entry.async_create_background_task(
            hass,
            async_update_device_info(hass, entry, ip_address),
            "wolf-update-device-info",
        )

    ism8.register_connection_callback(on_connection)

    # register the unloading callback
    entry.async_on_unload(lambda: async_close_server(server))

    # now setup the entities, regardless of connection
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry[WolfData]) -> bool:
    """Unload wolf integration"""
    _LOGGER.debug("Unloading ISM8")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


# HA will call this when unloading
async def async_close_server(server) -> None:
    _LOGGER.info("Releasing ISM8 network connection")
    server.close()
    server.close_clients()
    await server.wait_closed()


async def async_update_device_info(
    hass: HomeAssistant, entry: ConfigEntry[WolfData], ip_address: str
):
    """Update device information once connected: fetches some information from the
    ISM8-webportal. Most important is the ISM8 firmware version, which may restrict
    datapoints available to the integration. When the FW-version could be read,
    no unnecessary datapoints are initialized in Home Assistant.
    """

    if ip_address is None:
        return
    url = f"http://{ip_address}"

    sw_version = hw_version = serial_number = None
    try:
        session = async_get_clientsession(hass)
        async with session.get(url, timeout=10) as response:
            html = await response.text()
        match = re.search(r"FW-Version.*?(\d+\.\d+)", html)
        if match:
            sw_version = match.group(1)
        match = re.search(r"HW-Version.*?(\d+\.\d+)", html)
        if match:
            hw_version = match.group(1)
        match = re.search(r"<td>\s*(\w{12})\s*<\/td>", html)
        if match:
            serial_number = match.group(1)
        # Update the parent device with scraped info
        dr.async_get(hass).async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, entry.entry_id)},
            sw_version=sw_version,
            hw_version=hw_version,
            serial_number=serial_number,
            configuration_url=f"http://{ip_address}",
        )

        # Persist FW version so next boot knows it without connection
        if sw_version and sw_version != entry.runtime_data.fw_version:
            _LOGGER.info("detected FW change on ISM8. New sensors on next start/boot.")
            hass.config_entries.async_update_entry(
                entry,
                data={**entry.data, CONF_FW_VERSION: sw_version},
            )

    except Exception as err:
        _LOGGER.error("Unexpected error updating ISM8 device info: %s", err)
