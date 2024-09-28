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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """set up the custom component over the config entry"""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    _config = entry.data

    protocol: type[Ism8] = Ism8()
    hass.data[DOMAIN]["protocol"] = protocol
    coro = hass.loop.create_server(
        protocol.factory,
        host=_config[CONF_HOST],
        port=_config[CONF_PORT],
        family=socket.AF_INET,
    )
    task = hass.loop.create_task(coro)
    await task
    if task.done():
        _server = task.result()
        _lib_version = Ism8.get_version()
        _port = _config[CONF_PORT]
        for soc in _server.sockets:
            _ip = soc.getsockname()
            _LOGGER.debug(f"ISM-Lib {_lib_version} listening on {_ip}, {_port}")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Forward the setup to the different platforms.
    # for platform in PLATFORMS:
    # await hass.config_entries.async_forward_entry_setup(entry, platform)
    return True
