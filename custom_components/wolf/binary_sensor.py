"""
Support for Wolf heating via ISM8 adapter
"""
import logging
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from wolf_ism8 import Ism8
from .const import (
    DOMAIN,
    WOLF,
    WOLF_ISM8,
    SensorType,
)
from homeassistant.const import (
    CONF_DEVICES,
    STATE_PROBLEM,
    STATE_OK,
    STATE_ON,
    STATE_OFF,
    STATE_UNKNOWN,
)

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

    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]

    sensors = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) in config[CONF_DEVICES]:
            if ism8.get_type(nbr) in (
                SensorType.DPT_SWITCH,
                SensorType.DPT_BOOL,
                SensorType.DPT_ENABLE,
                SensorType.DPT_OPENCLOSE,
            ):
                if not ism8.is_writable(nbr):
                    sensors.append(WolfBinarySensor(ism8, nbr))
    async_add_entities(sensors)


class WolfBinarySensor(BinarySensorEntity):
    """Binary sensor representation for DPT_SWITCH, DPT_BOOL,
    DPT_ENABLE, DPT_OPENCLOSE types"""

    def __init__(self, ism8, dp_nbr):
        self.dp_nbr = dp_nbr
        self._device = ism8.get_device(dp_nbr)
        self._name = self._device + "_" + ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._unit = ism8.get_unit(dp_nbr)
        self._state = STATE_UNKNOWN
        self._ism8 = ism8
        _LOGGER.debug("setup BinarySensor no. %d as %s", self.dp_nbr, self._type)

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique_id of this sensor."""
        return str(self.dp_nbr)

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device)},
            "name": self._device,
            "manufacturer": WOLF,
            "model": WOLF_ISM8,
        }

    @property
    def state(self):
        """Return the state of the device."""
        if self.device_class == BinarySensorDeviceClass.PROBLEM:
            return STATE_PROBLEM if self.is_on else STATE_OK
        else:
            return STATE_ON if self.is_on else STATE_OFF

    @property
    def is_on(self) -> str:
        """Return true if the binary sensor is on."""
        return self._state

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
            return BinarySensorDeviceClass.MOVING
        else:
            return None

    async def async_update(self):
        """Return state"""
        self._state = self._ism8.read_sensor(self.dp_nbr)
        return
