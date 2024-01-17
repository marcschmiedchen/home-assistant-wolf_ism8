"""
Support for Wolf heating via ISM8 adapter
"""
import logging
from homeassistant.helpers.entity import Entity
from wolf_ism8 import Ism8
from .const import DOMAIN, WOLF, WOLF_ISM8
from homeassistant.const import STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)


class WolfEntity(Entity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
    dp_nbr represents the unique identifier of the up to 200 different
    sensors
    """

    _attr_has_entity_name = True

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        self.dp_nbr = dp_nbr
        self._ism8 = ism8
        self._device = ism8.get_device(dp_nbr)
        self._name = ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._state = STATE_UNKNOWN
        self._is_writable = ism8.is_writable(dp_nbr)
        if self._is_writable:
            self._value_range = ism8.get_value_area(dp_nbr)
            # if allowed range is a number, calculate min and max
            if isinstance(self._value_range[0], float) or isinstance(
                self._value_range[0], int
            ):
                self._max_value = max(self._value_range)
                self._min_value = min(self._value_range)
                self._step_value = abs(self._value_range[0] - self._value_range[1])
        _LOGGER.debug(
            "setup wolf entity  %s on %s as %s. Write access: %d",
            self._name,
            self._device,
            self._type,
            self._is_writable,
        )

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
        return {
            "identifiers": {(DOMAIN, self._device)},
            "name": self._device,
            "manufacturer": WOLF,
            "model": WOLF_ISM8,
        }

    @property
    def state(self):
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state, 1)
        return self._state

    async def async_update(self):
        """Return state"""
        self._state = self._ism8.read_sensor(self.dp_nbr)
        if self._state is None:
            self._state = STATE_UNKNOWN
        return
