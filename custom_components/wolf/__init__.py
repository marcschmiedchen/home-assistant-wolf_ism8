import asyncio
import logging
import re
from dataclasses import dataclass
from functools import partial

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
    fw_version: str = ""


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
        name=WOLF_ISM8,
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


def _remove_obsolete_devices(
    registry: dr.DeviceRegistry, entry: ConfigEntry[WolfData]
) -> None:
    """Remove old or deselected devices, so their entities don't linger."""

    selected = set(entry.data[CONF_DEVICES])
    for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
        # The ISM8 adapter itself is top-level. All others are via -> Keep it always.
        if device.via_device_id is None:
            continue
        identifier = list(device.identifiers)[0][1]
        if identifier in selected:
            continue
        _LOGGER.debug("removing deselected device %s", device.name)
        registry.async_remove_device(device.id)


@callback
def _on_connection(
    hass: HomeAssistant, entry: ConfigEntry[WolfData], ip_address: str
) -> None:
    """fires once connection to ISM8 is established. Req. data and scrape FW-version."""
    # after a HA restart, request  all entities once
    entry.runtime_data.protocol.request_all_datapoints()
    _LOGGER.debug("ISM8 connection to %s, starting info scraping", ip_address)
    entry.async_create_background_task(
        hass,
        async_update_device_info(hass, entry, ip_address),
        "wolf-update-device-info",
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry[WolfData]) -> bool:
    """set up the integration"""
    ism8 = Ism8()

    server = await hass.loop.create_server(
        ism8,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
    )

    entry.runtime_data = WolfData(
        protocol=ism8,
        server=server,
        fw_version=entry.data.get(CONF_FW_VERSION, ""),
    )

    # put all selected devices into the registry, and remove deselected devices
    registry = dr.async_get(hass)
    _add_devices(registry, entry)
    _remove_obsolete_devices(registry, entry)

    # register the connection callback -- starts scraping FW version, etc
    ism8.register_connection_callback(partial(_on_connection, hass, entry))
    # register the unloading callback, to free resources when unloaded
    entry.async_on_unload(partial(async_close_server, server, ism8))

    # now setup the entities, regardless of connection
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry[WolfData]) -> bool:
    """Unload wolf integration"""
    _LOGGER.debug("Unloading ISM8")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


# HA will call this when unloading
async def async_close_server(server: asyncio.Server, ism8: Ism8) -> None:
    _LOGGER.info("Releasing ISM8 network connection")
    # detach the protocol callbacks first: close_clients() makes asyncio call
    # connection_lost(), which would otherwise fire into the torn-down entities
    ism8.close()
    server.close()
    server.close_clients()
    await server.wait_closed()


async def async_update_device_info(
    hass: HomeAssistant, entry: ConfigEntry[WolfData], ip_address: str
):
    """Update device information once connected: fetches some information from the
    ISM8-webportal. Most important is the ISM8 firmware version, which may restrict
    datapoints available to the integration.
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
