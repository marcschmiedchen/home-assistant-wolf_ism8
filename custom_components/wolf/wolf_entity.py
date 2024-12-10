"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from wolf_ism8 import Ism8
from .const import DOMAIN, WOLF, WOLF_ISM8

from homeassistant.const import STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)


class WolfEntity(Entity):
    """
    Generic / Base Implementation of Wolf Heating System Sensor via ISM8-adapter.
    This class is used as a base class and shares all the functions and
    attributes which are the same in all Wolf Sensors.
    """

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        _LOGGER.debug(f"setup wolf entity {dp_nbr}")
        self.dp_nbr = dp_nbr
        self._ism8 = ism8
        self._device = ism8.get_device(dp_nbr)
        self._name = ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._state = STATE_UNKNOWN
        self._is_writable = ism8.is_writable(dp_nbr)

        if self._is_writable:
            self._value_range = ism8.get_value_range(dp_nbr)
            # if allowed range is a number, calculate min and max
            if isinstance(self._value_range[0], float) or isinstance(
                self._value_range[0], int
            ):
                self._max_value = max(self._value_range)
                self._min_value = min(self._value_range)
                self._step_value = abs(self._value_range[0] - self._value_range[1])

    async def async_added_to_hass(self) -> None:
        """Register callback for this datapoint when entity is added to HA."""
        self._ism8.register_callback(self.async_write_ha_state, self.dp_nbr)

    async def async_will_remove_from_hass(self) -> None:
        """un-register callback for this datapoint when entity is removed."""
        _LOGGER.debug(f"remove_from_hass (entity {self._name}) called")
        self._ism8.remove_callback(self.dp_nbr)

    @property
    def should_poll(self) -> bool:
        """Return False, because integration is now fully asnyc"""
        return False

    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def name(self) -> str:
        """Return the name of this entity."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique_id of this sensor."""
        return str(self.dp_nbr)

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device)},
            name=self._device,
            manufacturer=WOLF,
            model=WOLF_ISM8,
        )

    @property
    def native_value(self):
        """Return the state of the device."""
        value = self._ism8.read_sensor(self.dp_nbr)
        self._state = round(value, 2) if isinstance(value, float) else value
        _LOGGER.debug(f"value from ism: set DP {self.dp_nbr} to {self._state}")
        return self._state

    @property
    def available(self):
        return self._ism8.connected()
