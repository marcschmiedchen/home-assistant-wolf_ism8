import logging

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfEnergy
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.const import UnitOfVolumeFlowRate
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from wolf_ism8 import Ism8

from .const import SensorType
from .wolf_entity import WolfEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    performs setup of the analog sensors, expects a
    reference to an ism8-adapter via config_entry.runtime_data
    """
    ism8 = config_entry.runtime_data.protocol

    sensor_entities = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        if ism8.is_writable(nbr):
            continue
        if ism8.get_type(nbr) not in (
            SensorType.DPT_VALUE_TEMP,
            SensorType.DPT_VALUE_TEMPD,
            SensorType.DPT_VALUE_PRES,
            SensorType.DPT_SCALING,
            SensorType.DPT_POWER,
            SensorType.DPT_VALUE_VOLUME_FLOW,
            SensorType.DPT_FLOWRATE_M3,
            SensorType.DPT_HVACCONTRMODE,
            SensorType.DPT_ENERGY,
            SensorType.DPT_ENERGY_KWH,
        ):
            continue

        sensor_entities.append(WolfSensor(ism8, nbr))
    async_add_entities(sensor_entities)


class WolfSensor(WolfEntity, SensorEntity):
    """Implementation of Wolf Heating System Sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)

        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 2
        match self._type:
            case SensorType.DPT_VALUE_TEMP:
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
                self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            case SensorType.DPT_VALUE_TEMPD:
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
                self._attr_native_unit_of_measurement = UnitOfTemperature.KELVIN
            case SensorType.DPT_VALUE_PRES:
                self._attr_device_class = SensorDeviceClass.PRESSURE
                self._attr_native_unit_of_measurement = UnitOfPressure.PA
            case SensorType.DPT_SCALING:
                self._attr_device_class = SensorDeviceClass.POWER_FACTOR
                self._attr_native_unit_of_measurement = PERCENTAGE
            case SensorType.DPT_POWER:
                self._attr_device_class = SensorDeviceClass.POWER
                self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
            case SensorType.DPT_VALUE_VOLUME_FLOW:
                self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
                self._attr_native_unit_of_measurement = (
                    UnitOfVolumeFlowRate.LITERS_PER_HOUR
                )
                self._attr_suggested_display_precision = 0
            case SensorType.DPT_FLOWRATE_M3:
                self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
                self._attr_native_unit_of_measurement = (
                    UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
                )
                self._attr_suggested_display_precision = 0
            case SensorType.DPT_ENERGY:
                self._attr_device_class = SensorDeviceClass.ENERGY
                self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
                self._attr_state_class = SensorStateClass.TOTAL
                self._attr_suggested_display_precision = 0
            case SensorType.DPT_ENERGY_KWH:
                self._attr_device_class = SensorDeviceClass.ENERGY
                self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            case SensorType.DPT_HVACCONTRMODE:
                self._attr_device_class = SensorDeviceClass.ENUM
                self._attr_state_class = None
                self._attr_suggested_display_precision = None
