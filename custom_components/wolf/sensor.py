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
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from wolf_ism8 import Ism8
from .wolf_entity import WolfEntity
from . import WolfData
from .const import SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[WolfData],
    async_add_entities,
):
    """
    performs setup of the analog sensors, expects a
    reference to an ism8-adapter via config_entry.runtime_data
    """
    wolf_data = config_entry.runtime_data
    ism8 = wolf_data.protocol
    ism8_fw = wolf_data.sw_version

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
        if (ism8_fw is not None) and ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"sensor {nbr} not supported by firmware")
            continue
        sensor_entities.append(WolfSensor(ism8, nbr))
    async_add_entities(sensor_entities)


class WolfSensor(WolfEntity, SensorEntity):
    """Implementation of Wolf Heating System Sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)

        if self._type in (SENSOR_TYPES.DPT_VALUE_TEMP, SENSOR_TYPES.DPT_VALUE_TEMPD):
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        elif self._type == SENSOR_TYPES.DPT_VALUE_PRES:
            self._attr_device_class = SensorDeviceClass.PRESSURE
        elif self._type == SENSOR_TYPES.DPT_SCALING:
            self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        elif self._type == SENSOR_TYPES.DPT_POWER:
            self._attr_device_class = SensorDeviceClass.POWER
        elif self._type in (SENSOR_TYPES.DPT_ENERGY, SENSOR_TYPES.DPT_ENERGY_KWH):
            self._attr_device_class = SensorDeviceClass.ENERGY

        if self._type == SENSOR_TYPES.DPT_VALUE_TEMP:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._type == SENSOR_TYPES.DPT_VALUE_TEMPD:
            self._attr_native_unit_of_measurement = UnitOfTemperature.KELVIN
        elif self._type == SENSOR_TYPES.DPT_VALUE_PRES:
            self._attr_native_unit_of_measurement = UnitOfPressure.PA
        elif self._type == SENSOR_TYPES.DPT_SCALING:
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif self._type == SENSOR_TYPES.DPT_POWER:
            self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
        elif self._type == SENSOR_TYPES.DPT_VALUE_VOLUME_FLOW:
            self._attr_native_unit_of_measurement = "l/h"
        elif self._type == SENSOR_TYPES.DPT_FLOWRATE_M3:
            self._attr_native_unit_of_measurement = UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        elif self._type == SENSOR_TYPES.DPT_ENERGY:
            self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        elif self._type == SENSOR_TYPES.DPT_ENERGY_KWH:
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

        if self._type == SENSOR_TYPES.DPT_ENERGY:
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif self._type == SENSOR_TYPES.DPT_ENERGY_KWH:
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif self._type not in (
            SENSOR_TYPES.DPT_HVACMODE,
            SENSOR_TYPES.DPT_DHWMODE,
            SENSOR_TYPES.DPT_HVACCONTRMODE,
        ):
            self._attr_state_class = SensorStateClass.MEASUREMENT
