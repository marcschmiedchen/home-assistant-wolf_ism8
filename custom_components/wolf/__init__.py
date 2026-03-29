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

from .const import DOMAIN
from .const import WOLF
from .const import WOLF_ISM8

_LOGGER = logging.getLogger(__name__)


@dataclass
class WolfData:
    """Data for the Wolf integration."""

    protocol: Ism8
    server: asyncio.Server


PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.DATE,
    Platform.TIME,
]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[WolfData]
) -> bool:
    """set up the integration"""
    ism8 = Ism8()

    server = await hass.loop.create_server(
        ism8.factory,
        host=config_entry.data[CONF_HOST],
        port=config_entry.data[CONF_PORT],
        family=AF_INET,
    )

    config_entry.runtime_data = WolfData(protocol=ism8, server=server)

    device_registry = dr.async_get(hass)
    # Create the main ISM8 adapter device as connector for the other devices
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="ISM8 Adapter",
        manufacturer=WOLF,
        model=WOLF_ISM8,
    )

    @callback
    def on_connection(ip_address: str) -> None:
        """Handle connection to ISM8."""
        _LOGGER.debug("ISM8 connection to %s, starting info scraping", ip_address)
        config_entry.async_create_background_task(
            hass,
            async_update_device_info(hass, config_entry, ip_address),
            "wolf-update-device-info",
        )

    ism8.register_connection_callback(on_connection)

    # now loop over the configured devices and create them
    for device_name in config_entry.data[CONF_DEVICES]:
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, device_name)},
            name=device_name,
            via_device=(DOMAIN, config_entry.entry_id),
        )
    # register the unloading callback
    config_entry.async_on_unload(lambda: async_close_server(server))

    # now setup the entities, regardless of connection
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[WolfData]
) -> bool:
    """Unload wolf integration"""
    _LOGGER.debug("Unloading ISM8")
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def get_webportal_info(
    hass: HomeAssistant, ip_address: str | None
) -> tuple[str | None, str | None, str | None]:
    """Gets some information from the ISM-webportal. Most important is the ISM8 firmware
    version, which restricts the datapoints available to the integration. When FW
    version can be read, no unnecessary datapoints are initialized in Home Assistant.
    """


# HA will call this when unloading
async def async_close_server(server) -> None:
    _LOGGER.info("Releasing ISM8 network connection")
    server.close()
    server.close_clients()
    await server.wait_closed()


async def async_update_device_info(
    hass: HomeAssistant, config_entry: ConfigEntry[WolfData], ip_address: str
):
    """Update device information once connected: fetches some information from the
    ISM8-webportal. Most important is the ISM8 firmware version, which restricts the
    datapoints available to the integration. When the FW-version could be read,
    no unnecessary datapoints are initialized in Home Assistant.
    """
    _LOGGER.debug("ISM8 connected, fetching webportal info from %s", ip_address)

    if ip_address is None:
        return
    else:
        url = "http://" + ip_address

    try:
        session = async_get_clientsession(hass)
        async with session.get(url, timeout=10) as response:
            html = await response.text()
        match = re.search(r"FW-Version.*?(\d+\.\d+)", html)
        if match:
            sw_ver = match.group(1)
        match = re.search(r"HW-Version.*?(\d+\.\d+)", html)
        if match:
            hw_ver = match.group(1)
        match = re.search(r"<td>\s*(\w{12})\s*<\/td>", html)
        if match:
            ser_nbr = match.group(1)
        # Update the parent device with scraped info
        dr.async_get(hass).async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, config_entry.entry_id)},
            sw_version=sw_ver,
            hw_version=hw_ver,
            serial_number=ser_nbr,
            configuration_url=f"http://{ip_address}",
        )

    except Exception as err:
        _LOGGER.error("Unexpected error updating ISM8 device info: %s", err)
