"""
Support for Wolf heating via ISM8 adapter
"""
import logging

from homeassistant.const import (STATE_PROBLEM
                                 , STATE_OK
                                 , STATE_ON
                                 , STATE_OFF
                                 , STATE_UNKNOWN
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
            if ism8.get_type(nbr) in ("DPT_Switch",
                                      "DPT_Bool",
                                      "DPT_Enable",
                                      "DPT_OpenClose"
                                      ):
                sensors.append(WolfBinarySensor(ism8, nbr))

    async_add_entities(sensors)


class WolfBinarySensor(Entity):
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
        _LOGGER.debug('setup Sensor no. %d as %s', self.dp_nbr, self._type)

    @property
    def name(self):
        """Return the name of this sensor."""
        return (self._device + "_" + self._name).lower().replace(' ', '_')

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self.dp_nbr

    @property
    def state(self):
        """Return the state of the device."""
        if self.device_class == 'problem':
            return STATE_PROBLEM if self.is_on else STATE_OK
        else:
            return STATE_ON if self.is_on else STATE_OFF

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of the device."""
        if self._name == 'Stoerung':
            return 'problem'
        elif (self._name in ['Status Brenner / Flamme',
                             'Status E-Heizung']):
            return 'heat'
        elif (self._name in ['Status Heizkreispumpe',
                             'Status Speicherladepumpe',
                             'Status Mischerkreispumpe',
                             'Status Solarkreispumpe SKP1'
                             'Status Zubringer-/Heizkreispumpe']):
            return 'moving'
        else:
            return None

    async def async_update(self):
        """Return state"""
        self._state = self._ism8.read(self.dp_nbr)
        return
