"""
Support for Wolf heating via ISM8 adapter
"""

from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.const import CONF_DEVICES, UnitOfTemperature, PERCENTAGE
from .wolf_entity import WolfEntity
from wolf_ism8 import Ism8
from .const import DOMAIN, SENSOR_TYPES


async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    performs setup of the writeable number entities, needs a
    reference to an ism8-protocol implementation via hass.data
    """
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]

    numberEntityList = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        if not ism8.is_writable(nbr):
            continue
        if ism8.get_type(nbr) in (
            SENSOR_TYPES.DPT_VALUE_TEMP,
            SENSOR_TYPES.DPT_SCALING,
            SENSOR_TYPES.DPT_TEMPD,
        ):
            numberEntityList.append(WolfInputNumber(ism8, nbr))

    async_add_entities(numberEntityList)


class WolfInputNumber(WolfEntity, NumberEntity):
    """
    Number Entity for ISM8 datapoints which can
    be written to and which expect number values
    """

    @property
    def device_class(self) -> str:
        if self._type in (SENSOR_TYPES.DPT_VALUE_TEMP, SENSOR_TYPES.DPT_TEMPD):
            return NumberDeviceClass.TEMPERATURE
        elif self._type == SENSOR_TYPES.DPT_SCALING:
            return NumberDeviceClass.POWER_FACTOR

    @property
    def native_unit_of_measurement(self) -> str:
        if self._type in (SENSOR_TYPES.DPT_VALUE_TEMP, SENSOR_TYPES.DPT_TEMPD):
            return UnitOfTemperature.CELSIUS
        elif self._type == SENSOR_TYPES.DPT_SCALING:
            return PERCENTAGE

    @property
    def native_max_value(self):
        return self._max_value

    @property
    def native_min_value(self):
        return self._min_value

    @property
    def native_step(self):
        return self._step_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._ism8.send_dp_value(self.dp_nbr, value)
