"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.const import (
    CONF_DEVICES,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfVolumeFlowRate,
    PERCENTAGE,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorStateClass
from wolf_ism8 import Ism8
from .wolf_entity import WolfEntity
from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
):
    """
    performs setup of the analog sensors, expects a
    reference to an ism8-adapter via hass.data
    """
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]
    ism8_fw = hass.data[DOMAIN]["sw_version"]

    sensor_entities = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        if ism8.is_writable(nbr):
            continue
        if ism8.get_type(nbr) not in (
            SENSOR_TYPES.DPT_VALUE_TEMP,
            SENSOR_TYPES.DPT_VALUE_TEMPD,
            SENSOR_TYPES.DPT_VALUE_PRES,
            SENSOR_TYPES.DPT_SCALING,
            SENSOR_TYPES.DPT_POWER,
            SENSOR_TYPES.DPT_VALUE_VOLUME_FLOW,
            SENSOR_TYPES.DPT_FLOWRATE_M3,
            SENSOR_TYPES.DPT_HVACCONTRMODE,
            SENSOR_TYPES.DPT_ENERGY,
            SENSOR_TYPES.DPT_ENERGY_KWH,
        ):
            continue
        if ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"sensor {nbr} not supported by firmware")
            continue
        sensor_entities.append(WolfSensor(ism8, nbr))
    async_add_entities(sensor_entities)


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
        elif self._type in (SENSOR_TYPES.DPT_ENERGY, SENSOR_TYPES.DPT_ENERGY_KWH):
            return SensorDeviceClass.ENERGY

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
        elif self._type == SENSOR_TYPES.DPT_ENERGY:
            return UnitOfEnergy.WATT_HOUR
        elif self._type == SENSOR_TYPES.DPT_ENERGY_KWH:
            return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        if self._type in (
            SENSOR_TYPES.DPT_HVACMODE,
            SENSOR_TYPES.DPT_DHWMODE,
            SENSOR_TYPES.DPT_HVACCONTRMODE,
        ):
            return None
        elif self._type == SENSOR_TYPES.DPT_ENERGY:
            return SensorStateClass.TOTAL_INCREASING
        elif self._type == SENSOR_TYPES.DPT_ENERGY_KWH:
            return SensorStateClass.TOTAL_INCREASING
        else:
            return SensorStateClass.MEASUREMENT
