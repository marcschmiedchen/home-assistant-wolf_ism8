"""
Support for Wolf heating via ISM8 adapter
"""
import logging

from homeassistant.const import (
    STATE_UNKNOWN,
    TEMP_CELSIUS,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_PRESSURE,
    PRECISION_TENTHS
)
from homeassistant.helpers.entity import Entity
#from homeassistant.components.wolf import DOMAIN
from custom_components.wolf import DOMAIN
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """
    performs setup of the analog sensors, expects a
    reference to an ism8-adapter via hass.data
    """
    sensors = []
    ism8 = hass.data[DOMAIN]

    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) in discovery_info:
            if ism8.get_type(nbr) not in ("DPT_Switch",
                                          "DPT_Bool",
                                          "DPT_Enable",
                                          "DPT_OpenClose"
                                          ):
                sensors.append(WolfSensor(ism8, nbr))
    async_add_entities(sensors)


class WolfSensor(Entity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
        dp_nbr represents the unique identifier of the up to 200 different
        sensors
    """

    def __init__(self, ism8, dp_nbr):
        self.dp_nbr = dp_nbr
        self._device = ism8.get_device(dp_nbr)
        self._name = ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._unit = ism8.get_unit(dp_nbr)
        self._state = STATE_UNKNOWN
        self._ism8 = ism8
        _LOGGER.debug('Setup sensor no. %d as %s', self.dp_nbr, self._type)

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return (self._device + "_" + self._name).lower().replace(' ', '_')

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self.dp_nbr

    @property
    def state(self):
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state, 2)
        else:
            return self._state

    @property
    def device_class(self) -> str:
        """Return the state of the device."""
        if self._type == 'DPT_Value_Temp':
            return DEVICE_CLASS_TEMPERATURE
        elif self._type == 'DPT_Value_Pres':
            return DEVICE_CLASS_PRESSURE
        else:
            return ''

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        if self._type == 'DPT_Value_Temp':
            return TEMP_CELSIUS
        else:
            return self._unit

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    async def async_update(self):
        """Return state"""
        self._state = self._ism8.read(self.dp_nbr)
        return
