"""
Support for Wolf heating via ISM8 adapter
"""
import logging
from collections.abc import Callable
from homeassistant import config_entries
from homeassistant.const import (
    CONF_DEVICES,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
    PRECISION_TENTHS,
    TEMP_KELVIN,
    PRESSURE_PA,
    POWER_KILO_WATT,
    UnitOfVolumeFlowRate
)
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.typing import HomeAssistantType
from wolf_ism8 import Ism8
from .const import (
    DOMAIN,
    WOLF,
    WOLF_ISM8,
    SensorType,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable,
):
    """
    performs setup of the analog sensors, expects a
    reference to an ism8-adapter via hass.data
    """

    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]
    sensors = []
    for nbr in ism8.get_all_sensors().keys():

        if ism8.get_device(nbr) in config[CONF_DEVICES]:

            if ism8.get_type(nbr) == SensorType.DPT_SCALING:
                sensors.append(WolfScaleSensor(ism8, nbr))
            elif ism8.get_type(nbr) == SensorType.DPT_VALUE_TEMP:
                sensors.append(WolfTemperatureSensor(ism8, nbr))
            elif ism8.get_type(nbr) == SensorType.DPT_VALUE_TEMPD:
                sensors.append(WolfTemperatureSensor(ism8, nbr))
            elif ism8.get_type(nbr) == SensorType.DPT_VALUE_PRES:
                sensors.append(WolfPressureSensor(ism8, nbr))
            elif ism8.get_type(nbr) == SensorType.DPT_POWER:
                sensors.append(WolfPowerSensor(ism8, nbr))
            elif ism8.get_type(nbr) == SensorType.DPT_VALUE_VOLUME_FLOW:
                sensors.append(WolfFlowSensor1(ism8, nbr))
            elif ism8.get_type(nbr) == SensorType.DPT_TIMEOFDAY:
                continue  # :(None, None, type(time), None, None),
            elif ism8.get_type(nbr) == SensorType.DPT_DATE:
                continue  # :(None, None, type(datetime), None, None),
            elif ism8.get_type(nbr) == SensorType.DPT_FLOWRATE_M3:
                sensors.append(WolfAirFlowSensor(ism8, nbr))
                #continue  # :(-2147483647, 2147483647, type(int), 1 / 10000, "m3/h"),

    async_add_entities(sensors)


class WolfBaseSensor(Entity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
    dp_nbr represents the unique identifier of the up to 200 different
    sensors
    """

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        self.dp_nbr = dp_nbr
        self._ism8 = ism8
        self._device = ism8.get_device(dp_nbr)
        self._name = self._device+"_"+ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._step_value = ism8.get_step_value(dp_nbr)
        self._state = STATE_UNKNOWN
        _LOGGER.debug(
            "setup sensor no. %d on %s as %s", self.dp_nbr, self._device, self._type
        )

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
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

    async def async_update(self):
        """Return state"""
        self._state = self._ism8.read(self.dp_nbr)
        return


class WolfTemperatureSensor(WolfBaseSensor):
    """Implementing the temperature sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)
      
    @property
    def state(self):
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state, 1)
        return self._state

    @property
    def device_class(self) -> str:
        """Return the class of the device."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        if self._type == SensorType.DPT_VALUE_TEMP:
            return TEMP_CELSIUS
        elif self._type == SensorType.DPT_VALUE_TEMPD:
            return TEMP_KELVIN

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS


class WolfScaleSensor(WolfBaseSensor):
    """Implementing the temperature sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)
       
    @property
    def state(self):
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state)
        return self._state

    @property
    def device_class(self) -> str:
        """Return the state of the device."""
        return SensorDeviceClass.POWER_FACTOR


class WolfPressureSensor(WolfBaseSensor):
    """Implementing the temperature sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)
 
    @property
    def state(self) -> float:
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state)
        return self._state
        

    @property
    def device_class(self) -> str:
        """Return the class of the device."""
        return SensorDeviceClass.PRESSURE
        
    
    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return PRESSURE_PA
    
    
class WolfPowerSensor(WolfBaseSensor):
    """Implementing the power sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)

    @property
    def state(self) -> float:
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state,2)
        return self._state

    @property
    def device_class(self) -> str:
        """Return the class of the device."""
        return SensorDeviceClass.POWER
    
    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return POWER_KILO_WATT
    
class WolfFlowSensor1(WolfBaseSensor):
    """Implementing the power sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)

    @property
    def state(self) -> int:
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state)
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return "l/h"

class WolfAirFlowSensor(WolfBaseSensor):
    """Implementing the air flow sensors"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)
    
    @property
    def state(self) -> float:
        """Return the state of the device."""
        if isinstance(self._state, float):
            return round(self._state)
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
