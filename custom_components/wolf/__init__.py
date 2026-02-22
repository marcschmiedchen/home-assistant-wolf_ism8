"""
Support for Wolf heating system ISM via ISM8 adapter
"""

import logging
import asyncio
import re
from dataclasses import dataclass
from socket import AF_INET

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from wolf_ism8 import Ism8
from .const import DOMAIN, WOLF, WOLF_ISM8
from homeassistant.const import CONF_DEVICES

_LOGGER = logging.getLogger(__name__)

@dataclass
class WolfData:
    """Data to share between platforms."""

    protocol: Ism8
    servertask: asyncio.Task
    server: asyncio.AbstractServer
    sw_version: str | None = None
    hw_version: str | None = None
    serno: str | None = None
    ism8_ip_address: str = None

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.DATE,
    Platform.TIME,
]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry[WolfData]) -> bool:
    """set up the custom component over the config entry"""
    ism8 = Ism8()

    server = await hass.loop.create_server(
        ism8.factory,
        host=config_entry.data[CONF_HOST],
        port=config_entry.data[CONF_PORT],
        family=AF_INET,
    )

    config_entry.runtime_data = WolfData(
        protocol=ism8,
        servertask=None,
        server=server,
    )

    async def _async_scrape_once_connected():
        """Wait for connection and scrape info."""
        _LOGGER.debug("Background task started: waiting for ISM8 connection")
        try:
            async with asyncio.timeout(30):
                while not ism8.connected():
                    await asyncio.sleep(5)
                _LOGGER.debug("ISM8 connected, fetching webportal info")
                config_entry.runtime_data.ism8_ip_address = ism8.get_remote_ip_adress()
                await get_webportal_info(hass, config_entry)
        except TimeoutError:
            _LOGGER.info("Timeout waiting for ISM8 to connect for info scraping")
        except Exception as err:
            _LOGGER.error("Unexpected error in background scraping task: %s", err)

    # Start scraping in the background so setup can continue
    config_entry.async_create_background_task(hass, _async_scrape_once_connected(), "wolf-scrape-info")

    # now setup the entities, regardless of connection
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry[WolfData]) -> bool:
    """Unload wolf integration"""
    _LOGGER.debug("Unloading ISM8")
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unload_ok:
        wolf_data = config_entry.runtime_data
        _LOGGER.info("Releasing ISM8 network connection")
        if wolf_data.protocol._transport is not None:
            wolf_data.protocol._transport.close()
        wolf_data.server.close()

    return unload_ok


async def get_webportal_info(hass: HomeAssistant, config_entry: ConfigEntry[WolfData]) -> None:
    """Gets some information from the ISM-webportal. Most important is the ISM8 firmware
    version, which restricts the datapoints available to the integration. When FW
    version can be read, no uneccesary datapoints are initialized in Home Assistant.
    """
    wolf_data = config_entry.runtime_data
    wolf_data.ism8_ip_address
    url = None
    if wolf_data.ism8_ip_address is not None:
        url = "http://" + wolf_data.ism8_ip_address
        try:
            _LOGGER.debug(f"trying to scrape FW-Version from {url}")
            session = async_get_clientsession(hass)
            async with session.get(url, timeout=10) as response:
                html = await response.text()

            match = re.search(r"FW-Version.*?(\d+\.\d+)", html)
            if match:
                wolf_data.sw_version = match.group(1)
                _LOGGER.debug(f"extracted FW: {wolf_data.sw_version}")

            match = re.search(r"HW-Version.*?(\d+\.\d+)", html)
            if match:
                wolf_data.hw_version = match.group(1)
                _LOGGER.debug(f"extracted HW: {wolf_data.hw_version}")

            match = re.search(r"<td>\s*(\w{12})\s*<\/td>", html)
            if match:
                wolf_data.serno = match.group(1)
                _LOGGER.debug(f"extracted serNo: {wolf_data.serno}")

        except Exception as e:
            _LOGGER.info("Could not gather info on ISM8: %s", e)

    device_registry = dr.async_get(hass)
    for device_name in config_entry.data[CONF_DEVICES]:
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, device_name)},
            name=device_name,
            manufacturer=WOLF,
            model=WOLF_ISM8,
            sw_version=wolf_data.sw_version,
            hw_version=wolf_data.hw_version,
            serial_number=wolf_data.serno,
            configuration_url=url if wolf_data.ism8_ip_address else None,
        )
    return
