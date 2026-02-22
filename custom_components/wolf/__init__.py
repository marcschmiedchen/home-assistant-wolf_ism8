"""
Support for Wolf heating system ISM via ISM8 adapter
"""

import logging
import asyncio
import re
from dataclasses import dataclass
from socket import AF_INET
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.helpers import device_registry as dr
from wolf_ism8 import Ism8
from .const import DOMAIN, CONF_DEVICES, WOLF, WOLF_ISM8

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

    coro = hass.loop.create_server(
        ism8.factory,
        host=config_entry.data[CONF_HOST],
        port=config_entry.data[CONF_PORT],
        family=AF_INET,
    )
    _task = hass.loop.create_task(coro)
    await _task
    if _task.done():
        _LOGGER.info("Waiting for ISM8 to connect")

        # yield some time to get the ISM8 connect to the host
        i = 0
        while i < 10 and not ism8.connected():
            i = i + 1
            _LOGGER.debug("waiting up to 20s for ISM8 to connect...")
            await asyncio.sleep(2)

        config_entry.runtime_data = WolfData(
            protocol=ism8,
            servertask=_task,
            server=_task.result(),
        )

        if ism8.connected():
            # This tries to read the FW-version from the ISM8-Webportal.
            # If this fails, only FW1.00 functionality gets enabled in HA.
            await get_webportal_info(hass, config_entry)

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
    remote_ip_address = wolf_data.protocol.get_remote_ip_adress()
    if remote_ip_address is not None:
        url = "http://" + remote_ip_address
        try:
            _LOGGER.debug(f"trying to scrape FW-Version from {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = str(await response.text())

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

        except aiohttp.ClientConnectorError as e:
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
            configuration_url=url if remote_ip_address else None,
        )
    return
