import logging

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from wolf_ism8 import Ism8

from .const import KEEPALIVE_WATCHDOG_TIMEOUT
from .const import SensorType
from .wolf_entity import WolfEntity
from .wolf_entity import wolf_datapoint_filter
from .wolf_entity import wolf_remove_entity

_LOGGER = logging.getLogger(__name__)

KEEPALIVE_NAME = "Keepalive_Ping"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    performs setup of the binary sensors, needs a
    reference to an ism8-protocol implementation via config_entry.runtime_data
    """
    ism8 = config_entry.runtime_data.protocol

    binary_sensor_entities = []
    for nbr in ism8.get_all_sensors().keys():
        # check if this sensor should be added to THIS platform
        if wolf_datapoint_filter(
            nbr,
            config_entry=config_entry,
            platforms=(
                SensorType.DPT_SWITCH,
                SensorType.DPT_BOOL,
                SensorType.DPT_ENABLE,
                SensorType.DPT_OPENCLOSE,
            ),
            writable=False,
        ):
            if ism8.get_name(nbr) == KEEPALIVE_NAME:
                binary_sensor_entities.append(WolfKeepaliveSensor(ism8, nbr))
            else:
                binary_sensor_entities.append(WolfBinarySensor(ism8, nbr))
        else:
            # an entity of an earlier setup this config no longer wants
            wolf_remove_entity(hass, nbr)
    async_add_entities(binary_sensor_entities)


class WolfBinarySensor(WolfEntity, BinarySensorEntity):
    """Binary sensor representation for DPT_SWITCH, DPT_BOOL,
    DPT_ENABLE, DPT_OPENCLOSE types"""

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)

        match self._attr_name:
            case "Stoerung":
                self._attr_device_class = BinarySensorDeviceClass.PROBLEM
            case "Status Brenner / Flamme" | "Status E-Heizung":
                self._attr_device_class = BinarySensorDeviceClass.HEAT
            case (
                "Status Heizkreispumpe"
                | "Status Speicherladepumpe"
                | "Status Mischerkreispumpe"
                | "Status Solarkreispumpe SKP1"
                | "Status Zubringer-/Heizkreispumpe"
            ):
                self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool:
        """Return the state of the device."""
        return bool(self._ism8.read_sensor(self.dp_nbr))


class WolfKeepaliveSensor(WolfBinarySensor):
    """The keepalive datapoint reflects whether the ISM8 is talking to us.
    Unlike all other entities it stays available and turns off when the
    connection is lost, so automations can react on it. It also arms the
    protocol's inactivity watchdog: dp 767 proves the firmware keeps sending
    while idle, so only then may silence be read as a lost connection."""

    _watchdog_armed = False

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        """on while the ISM8 connection is alive (keepalives arriving)"""
        return self._ism8.connected()

    async def async_added_to_hass(self) -> None:
        """Register the arming callback. Deliberately not calling super(): the
        base class would write the state through the same single callback slot
        per datapoint and overwrite this wrapper."""
        self._ism8.register_callback(self._on_keepalive, self.dp_nbr)
        if self._ism8.read_sensor(self.dp_nbr) is not None:
            # restart onto a live connection: arm without waiting for the next ping
            self._arm_watchdog("keepalive already cached")

    @callback
    def _on_keepalive(self) -> None:
        """refresh state and arm the watchdog"""
        self._arm_watchdog("keepalive received")
        if not self._ism8.connected():
            _LOGGER.debug("ISM8 disconnected, turning keepalive sensor off")
        self.async_write_ha_state()

    def _arm_watchdog(self, reason: str) -> None:
        """arms the protocol watchdog once, and logs it only that one time"""
        if self._watchdog_armed:
            return
        # set the flag first: if the call fails, one log beats one per keepalive
        self._watchdog_armed = True
        _LOGGER.debug(
            "arming ISM8 inactivity watchdog (%ss): %s",
            KEEPALIVE_WATCHDOG_TIMEOUT,
            reason,
        )
        self._ism8.set_watchdog_timeout(KEEPALIVE_WATCHDOG_TIMEOUT)
