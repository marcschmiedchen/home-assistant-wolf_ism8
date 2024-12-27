"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from wolf_ism8 import Ism8
from .wolf_entity import WolfEntity
from .const import DOMAIN, SENSOR_TYPES
from homeassistant.const import CONF_DEVICES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
):
    """
    performs setup of the binary sensors, needs a
    reference to an ism8-protocol implementation via hass.data
    """
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]
    ism8_fw = hass.data[DOMAIN]["sw_version"]

    binary_sensor_entities = []
    for nbr in ism8.get_all_sensors().keys():
        # only add sensors which were enabled in the config
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        # only add sensors which are binary
        if ism8.get_type(nbr) not in (
            SENSOR_TYPES.DPT_SWITCH,
            SENSOR_TYPES.DPT_BOOL,
            SENSOR_TYPES.DPT_ENABLE,
            SENSOR_TYPES.DPT_OPENCLOSE,
        ):
            continue
        # only add sensors which are not writable
        if ism8.is_writable(nbr):
            continue
        # only add sensor if it's supported by the firmware already
        if ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"sensor {nbr} not supported by firmware")
            continue
        binary_sensor_entities.append(WolfBinarySensor(ism8, nbr))

    async_add_entities(binary_sensor_entities)


class WolfBinarySensor(WolfEntity, BinarySensorEntity):
    """Binary sensor representation for DPT_SWITCH, DPT_BOOL,
    DPT_ENABLE, DPT_OPENCLOSE types"""

    @property
    def is_on(self) -> bool:
        """Return binary sensor state; invert logic for problem sensors."""
        self._state = self._ism8.read_sensor(self.dp_nbr)
        # _LOGGER.debug(f"binary value from ism: set DP {self.dp_nbr} to {self._state}")
        return bool(self._state)

    @property
    def device_class(self):
        """Return the class of the device."""
        if self._name == "Stoerung":
            return BinarySensorDeviceClass.PROBLEM
        elif self._name in ["Status Brenner / Flamme", "Status E-Heizung"]:
            return BinarySensorDeviceClass.HEAT
        elif self._name in [
            "Status Heizkreispumpe",
            "Status Speicherladepumpe",
            "Status Mischerkreispumpe",
            "Status Solarkreispumpe SKP1",
            "Status Zubringer-/Heizkreispumpe",
        ]:
            return BinarySensorDeviceClass.RUNNING
        else:
            return None
