"""
Support for Wolf heating system ISM via ISM8 adapter
"""

import logging
import asyncio
import re
from socket import AF_INET
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from wolf_ism8 import Ism8
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.DATE,
    Platform.TIME,
]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """set up the custom component over the config entry"""
    hass.data.setdefault(DOMAIN, {})

    ism8 = Ism8()
    hass.data[DOMAIN]["protocol"] = ism8

    coro = hass.loop.create_server(
        ism8.factory,
        host=config_entry.data[CONF_HOST],
        port=config_entry.data[CONF_PORT],
        family=AF_INET,
    )
    _task = hass.loop.create_task(coro)
    await _task
    if _task.done():
        hass.data[DOMAIN]["servertask"] = _task
        hass.data[DOMAIN]["server"] = _task.result()
        hass.data[DOMAIN]["sw_version"] = None
        hass.data[DOMAIN]["hw_version"] = None
        hass.data[DOMAIN]["serno"] = None
        _LOGGER.info("Waiting for ISM8 to connect")

        # yield some time to get the ISM8 connect to the host
        i = 0
        while i < 15 and not ism8.connected():
            i = i + 1
            _LOGGER.debug("waiting up to 30s for ISM8 to connect...")
            await asyncio.sleep(2)

        if ism8.connected():
            # This tries to read the FW-version from the ISM8-Webportal.
            # If this fails, only FW1.00 functionality gets enabled in HA.
            await get_webportal_info(hass, ism8.get_remote_ip_adress())

        # now setup the entities, regardless of connection
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
        return True


async def async_unload_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Unload wolf integration"""
    _LOGGER.debug("Unloading ISM8")
    unload_ok = await hass.config_entries.async_unload_platforms(config, PLATFORMS)
    _server = hass.data[DOMAIN]["server"]
    _ism8 = hass.data[DOMAIN]["protocol"]
    if _server is not None:
        _LOGGER.info("Releasing ISM8 network connection")
        if _ism8._transport is not None:
            _ism8._transport.close()
        _server.close()
    hass.data[DOMAIN].pop("server")
    hass.data[DOMAIN].pop("servertask")
    hass.data[DOMAIN].pop("hw_version")
    hass.data[DOMAIN].pop("sw_version")
    hass.data[DOMAIN].pop("serno")
    hass.data[DOMAIN].pop("protocol")
    return unload_ok


async def get_webportal_info(hass: HomeAssistant, remote_ip_address: str) -> None:
    """Gets some information from the ISM-webportal. Most important is the ISM8 firmware
    version, which restricts the datapoints available to the integration. When FW
    version can be read, no uneccesary datapoints are initialized in Home Assistant.
    """
    if remote_ip_address is not None:
        url = "http://" + remote_ip_address
        try:
            _LOGGER.debug(f"trying to scrape FW-Version from {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = str(await response.text())

            match = re.search(r"FW-Version.*?(\d+\.\d+)", html)
            if match:
                hass.data[DOMAIN]["sw_version"] = match.group(1)
                _LOGGER.debug(f"extracted FW: {hass.data[DOMAIN]['sw_version']}")

            match = re.search(r"HW-Version.*?(\d+\.\d+)", html)
            if match:
                hass.data[DOMAIN]["hw_version"] = match.group(1)
                _LOGGER.debug(f"extracted HW: {hass.data[DOMAIN]['hw_version']}")

            match = re.search(r"<td>\s*(\w{12})\s*<\/td>", html)
            if match:
                hass.data[DOMAIN]["serno"] = match.group(1)
                _LOGGER.debug(f"extracted serNo: {hass.data[DOMAIN]['serno']}")

        except aiohttp.ClientConnectorError as e:
            print("Could not gather info on ISM8.")
            print("Error code: ", e.errno)
            _LOGGER.info("Could not get ISM-IP-address to extract FW-Info.")
    return
