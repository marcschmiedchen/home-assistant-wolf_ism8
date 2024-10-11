"""
Support for Wolf heating system ISM via ISM8 adapter
"""

import logging
import socket

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


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """set up the custom component over the config entry"""
    hass.data.setdefault(DOMAIN, {})

    protocol = Ism8()
    _LOGGER.debug(f"ISM-Lib {protocol.get_version()}")
    hass.data[DOMAIN]["protocol"] = protocol
    coro = hass.loop.create_server(
        protocol.factory,
        host=config_entry.data[CONF_HOST],
        port=config_entry.data[CONF_PORT],
        family=socket.AF_INET,
    )
    _task = hass.loop.create_task(coro)
    await _task
    if _task.done():
        _server = _task.result()
        hass.data[DOMAIN]["servertask"] = _task
        hass.data[DOMAIN]["server"] = _server
        for soc in _server.sockets:
            _ip = soc.getsockname()
            _LOGGER.debug(f"Listening on {_ip}")
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload ISM8."""
    _ism8 = hass.data[DOMAIN]["protocol"]
    _task = hass.data[DOMAIN]["servertask"]
    _server = hass.data[DOMAIN]["server"]
    if _ism8.connected():
        _LOGGER.info("Releasing ISM8 network connection")
        _ism8._transport.close()
        _server.close()
        _task.cancel()
    return True
