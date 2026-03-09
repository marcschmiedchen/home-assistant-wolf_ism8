"""
Support for Wolf heating system ISM via ISM8 adapter
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from socket import AF_INET

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES, CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from wolf_ism8 import Ism8

from .const import DOMAIN, WOLF, WOLF_ISM8

_LOGGER = logging.getLogger(__name__)


@dataclass
class WolfData:
    """Data to share between platforms."""

    protocol: Ism8
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


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[WolfData]
) -> bool:
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
        server=server,
    )

    device_registry = dr.async_get(hass)
    # Create the main ISM8 adapter device
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="ISM8 Adapter",
        manufacturer=WOLF,
        model=WOLF_ISM8,
    )

    for device_name in config_entry.data[CONF_DEVICES]:
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, device_name)},
            name=device_name,
            via_device=(DOMAIN, config_entry.entry_id),
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
                await get_webportal_info(hass, config_entry.runtime_data)

                # Update the parent device with scraped info
                dr.async_get(hass).async_get_or_create(
                    config_entry_id=config_entry.entry_id,
                    identifiers={(DOMAIN, config_entry.entry_id)},
                    sw_version=config_entry.runtime_data.sw_version,
                    hw_version=config_entry.runtime_data.hw_version,
                    serial_number=config_entry.runtime_data.serno,
                    configuration_url=f"http://{config_entry.runtime_data.ism8_ip_address}"
                    if config_entry.runtime_data.ism8_ip_address
                    else None,
                )
        except TimeoutError:
            _LOGGER.info("Timeout waiting for ISM8 to connect for info scraping")
        except Exception as err:
            _LOGGER.error("Unexpected error in background scraping task: %s", err)

    # Start scraping in the background so setup can continue
    config_entry.async_create_background_task(
        hass, _async_scrape_once_connected(), "wolf-scrape-info"
    )
    # now setup the entities, regardless of connection
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[WolfData]
) -> bool:
    """Unload wolf integration"""
    _LOGGER.debug("Unloading ISM8")
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        wolf_data = config_entry.runtime_data
        _LOGGER.info("Releasing ISM8 network connection")
        wolf_data.server.close()
        result = wolf_data.server.close_clients()
        # Check if the result is a coroutine before awaiting it
        if asyncio.iscoroutine(result):
            await result
        await wolf_data.server.wait_closed()
    return unload_ok


async def get_webportal_info(hass: HomeAssistant, wolf_data) -> None:
    """Gets some information from the ISM-webportal. Most important is the ISM8 firmware
    version, which restricts the datapoints available to the integration. When FW
    version can be read, no unnecessary datapoints are initialized in Home Assistant.
    """
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

    return
