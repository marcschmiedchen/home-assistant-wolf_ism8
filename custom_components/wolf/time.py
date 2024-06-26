"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.components.time import TimeEntity
from homeassistant.const import CONF_DEVICES
from .wolf_entity import WolfEntity
from wolf_ism8 import Ism8
from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    performs setup of the writeable number entities, needs a
    reference to an ism8-protocol implementation via hass.data
    """
    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]

    timeEntityList = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) not in config[CONF_DEVICES]:
            continue
        if not ism8.is_writable(nbr):
            continue
        if ism8.get_type(nbr) == SENSOR_TYPES.DPT_TIMEOFDAY:
            timeEntityList.append(WolfTime(ism8, nbr))

    async_add_entities(timeEntityList)


class WolfTime(WolfEntity, TimeEntity):
    """
    Time Entity for ISM8 datapoints which can be written to
    """

    async def async_set_value(self, time) -> None:
        """Update the current value."""
        _LOGGER.debug(f"send dp {self.dp_nbr}: {time}")
        self._ism8.send_dp_value(self.dp_nbr, time)
