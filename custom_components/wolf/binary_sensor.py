import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from wolf_ism8 import Ism8

from . import WolfData
from .const import SensorType
from .wolf_entity import WolfEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[WolfData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    performs setup of the binary sensors, needs a
    reference to an ism8-protocol implementation via config_entry.runtime_data
    """
    ism8 = config_entry.runtime_data.protocol
    ism8_fw = config_entry.runtime_data.sw_version

    binary_sensor_entities = []
    for nbr in ism8.get_all_sensors().keys():
        # only add sensors which were enabled in the config
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        # only add sensors which are binary
        if ism8.get_type(nbr) not in (
            SensorType.DPT_SWITCH,
            SensorType.DPT_BOOL,
            SensorType.DPT_ENABLE,
            SensorType.DPT_OPENCLOSE,
        ):
            continue
        # only add sensors which are not writable
        if ism8.is_writable(nbr):
            continue
        # only add sensor if it's supported by the firmware already
        if (ism8_fw is not None) and ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"sensor {nbr} not supported by firmware")
            continue
        binary_sensor_entities.append(WolfBinarySensor(ism8, nbr))
    async_add_entities(binary_sensor_entities)


class WolfBinarySensor(WolfEntity, BinarySensorEntity):
    """Binary sensor representation for DPT_SWITCH, DPT_BOOL,
    DPT_ENABLE, DPT_OPENCLOSE types"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)

        if self._attr_name == "Stoerung":
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        elif self._attr_name in ["Status Brenner / Flamme", "Status E-Heizung"]:
            self._attr_device_class = BinarySensorDeviceClass.HEAT
        elif self._attr_name in [
            "Status Heizkreispumpe",
            "Status Speicherladepumpe",
            "Status Mischerkreispumpe",
            "Status Solarkreispumpe SKP1",
            "Status Zubringer-/Heizkreispumpe",
        ]:
            self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool:
        """Return the state of the device."""
        return bool(self._ism8.read_sensor(self.dp_nbr))
