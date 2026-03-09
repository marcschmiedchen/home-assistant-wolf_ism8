"""
Support for Wolf heating via ISM8 adapter
"""

import logging

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import WolfData
from .const import SENSOR_TYPES
from .wolf_entity import WolfEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[WolfData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    performs setup of the time entities, needs a
    reference to an ism8-protocol implementation via config_entry.runtime_data
    """
    ism8 = config_entry.runtime_data.protocol
    ism8_fw = config_entry.runtime_data.sw_version

    time_entities = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        if ism8.get_type(nbr) != SENSOR_TYPES.DPT_TIMEOFDAY:
            continue
        if not ism8.is_writable(nbr):
            continue
        if (ism8_fw is not None) and ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"sensor {nbr} not supported by firmware")
            continue
        time_entities.append(WolfTime(ism8, nbr))

    async_add_entities(time_entities)


class WolfTime(WolfEntity, TimeEntity):
    """
    Time Entity for ISM8 datapoints which can be written to
    """

    @property
    def native_value(self):
        """Return the state of the device."""
        return self._ism8.read_sensor(self.dp_nbr)

    async def async_set_value(self, time) -> None:
        """Update the current value."""
        _LOGGER.debug(f"send dp {self.dp_nbr}: {time}")
        self._ism8.send_dp_value(self.dp_nbr, time)
