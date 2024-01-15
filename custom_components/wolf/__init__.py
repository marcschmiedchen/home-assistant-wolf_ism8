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
        for soc in _server.sockets:
            _LOGGER.debug(
                "Listening for ISM8 on %s : %s", soc.getsockname(), _config[CONF_PORT]
            )

    # Forward the setup to the different platforms.
    for sensor in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, sensor)
        )

    return True
