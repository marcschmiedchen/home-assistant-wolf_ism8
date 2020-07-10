"""
Support for Wolf heating system ISM via ISM8 adapter
"""
REQUIREMENTS = ['wolf_ism8>=0.51']

import logging
import socket
import asyncio
import voluptuous as vol
from homeassistant.const import (
    CONF_NAME, CONF_DEVICES, CONF_HOST, CONF_PORT)
from homeassistant.helpers.discovery import load_platform
import homeassistant.helpers.config_validation as cv
from wolf_ism8.ism8 import Ism8

_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(logging.DEBUG)

WOLF_DEVICES = ['HG1', 'HG2', 'HG3', 'HG4',
                'BM1', 'BM2', 'BM3', 'BM4',
                'MM1', 'MM2','MM3',
                'KM','SM', 'CWL', 'BWL']

DEFAULT_WOLF_DEVICE = 'HG1'
DEFAULT_PORT = 12004
DOMAIN = 'wolf'

WOLF_SCHEMA = vol.Schema({
    vol.Optional(CONF_HOST, default=''): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_NAME, default=DOMAIN): cv.string,
    vol.Optional(CONF_DEVICES, default=[DEFAULT_WOLF_DEVICE]): 
    vol.All(cv.ensure_list, [vol.In(WOLF_DEVICES)]),
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: WOLF_SCHEMA,
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Get all the config values, initialize network connection and add sensors"""    
    _conf = config.get(DOMAIN)

    myProtocol = Ism8()
    hass.data[DOMAIN] = myProtocol
    coro=hass.loop.create_server(
            myProtocol.factory,
            host=_conf.get(CONF_HOST), 
            port=_conf.get(CONF_PORT), 
            family=socket.AF_INET
            )  
    task=hass.loop.create_task(coro)
    
    await task
    if task.done():
        _server=task.result()
        for s in _server.sockets:
            _LOGGER.debug('Listening for ISM8 on {} : {}'.format(s.getsockname(),_conf.get(CONF_PORT)))
    
    #call sensor_init with DEVICES as indication for which DP to initialize
    load_platform(hass, 'sensor', DOMAIN, _conf.get(CONF_DEVICES), config)
    load_platform(hass, 'binary_sensor', DOMAIN, _conf.get(CONF_DEVICES), config)
    
    return True

