import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from wolf_ism8 import Ism8
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WolfEntity(Entity):
    """
    Generic / Base Implementation of Wolf Heating System Sensor via ISM8-adapter.
    This class is used as a base class and shares all the functions and
    attributes which are the same in all Wolf Sensors.
    """

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        _LOGGER.debug(f"setup wolf entity {dp_nbr}")
        self.dp_nbr = dp_nbr
        self._ism8 = ism8
        self._type = ism8.get_type(dp_nbr)
        self._device = ism8.get_device(dp_nbr)
        self._attr_name = ism8.get_name(dp_nbr)
        self._is_writable = ism8.is_writable(dp_nbr)
        self._attr_unique_id = str(self.dp_nbr)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device)},
            name=self._device,
        )

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
        """un-register callback and delete ISM8-reference when entity is removed."""
        _LOGGER.debug(f"remove_from_hass (entity {self._attr_name}) called")
        self._ism8.remove_callback(self.dp_nbr)
        self._ism8 = None

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the device."""
        value = self._ism8.read_sensor(self.dp_nbr)
        return round(value, 4) if isinstance(value, float) else value

    @property
    def available(self) -> bool:
        """Return the availability"""
        return self._ism8.connected()
