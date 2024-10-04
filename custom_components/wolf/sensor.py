"""
Support for Wolf heating via ISM8 adapter
"""

from homeassistant.const import (
    CONF_DEVICES,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfPower,
    UnitOfVolumeFlowRate,
    PERCENTAGE,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorDeviceClass
from wolf_ism8 import Ism8
from .wolf_entity import WolfEntity
from .const import DOMAIN, SENSOR_TYPES


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
):
    """
    performs setup of the analog sensors, expects a
    reference to an ism8-adapter via hass.data
    """

    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]
    sensors = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) in config[CONF_DEVICES] and not ism8.is_writable(nbr):
            if ism8.get_type(nbr) in (
                SENSOR_TYPES.DPT_VALUE_TEMP,
                SENSOR_TYPES.DPT_VALUE_TEMPD,
                SENSOR_TYPES.DPT_VALUE_PRES,
                SENSOR_TYPES.DPT_SCALING,
                SENSOR_TYPES.DPT_POWER,
                SENSOR_TYPES.DPT_VALUE_VOLUME_FLOW,
                SENSOR_TYPES.DPT_FLOWRATE_M3,
                SENSOR_TYPES.DPT_HVACCONTRMODE,
            ):
                sensors.append(WolfSensor(ism8, nbr))
    async_add_entities(sensors)


class WolfSensor(WolfEntity, SensorEntity):
    """Implementation of Wolf Heating System Sensors"""

    @property
    def device_class(self) -> str:
        if self._type in (SENSOR_TYPES.DPT_VALUE_TEMP, SENSOR_TYPES.DPT_VALUE_TEMPD):
            return SensorDeviceClass.TEMPERATURE
        elif self._type == SENSOR_TYPES.DPT_VALUE_PRES:
            return SensorDeviceClass.PRESSURE
        elif self._type == SENSOR_TYPES.DPT_SCALING:
            return SensorDeviceClass.POWER_FACTOR
        elif self._type == SENSOR_TYPES.DPT_POWER:
            return SensorDeviceClass.POWER

    @property
    def native_unit_of_measurement(self) -> str:
        if self._type == SENSOR_TYPES.DPT_VALUE_TEMP:
            return UnitOfTemperature.CELSIUS
        elif self._type == SENSOR_TYPES.DPT_VALUE_TEMPD:
            return UnitOfTemperature.KELVIN
        elif self._type == SENSOR_TYPES.DPT_VALUE_PRES:
            return UnitOfPressure.PA
        elif self._type == SENSOR_TYPES.DPT_SCALING:
            return PERCENTAGE
        elif self._type == SENSOR_TYPES.DPT_POWER:
            return UnitOfPower.KILO_WATT
        elif self._type == SENSOR_TYPES.DPT_VALUE_VOLUME_FLOW:
            return "l/h"
        elif self._type == SENSOR_TYPES.DPT_FLOWRATE_M3:
            return UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
