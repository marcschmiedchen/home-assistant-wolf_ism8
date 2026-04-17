import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SensorType
from .wolf_entity import WolfEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """performs setup of the <select> entities"""

    ism8 = config_entry.runtime_data.protocol

    select_entities = []
    for nbr in ism8.get_all_sensors().keys():
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        if not ism8.is_writable(nbr):
            continue
        if ism8.get_type(nbr) != SensorType.DPT_SWITCH:
            continue
        # those are DPT_SWITCH, but trigger (button-)entities
        if nbr in (193, 194):
            _LOGGER.debug(f"ignoring {ism8.get_name(nbr)} as switch")
            continue
        # those are DPT_SWITCH, but are select entities, not on/off switches
        if ism8.get_name(nbr)[-1] in ("1", "2", "3"):
            _LOGGER.debug(f"ignoring {ism8.get_name(nbr)} as switch")
            continue
        select_entities.append(WolfSwitch(ism8, nbr))

    async_add_entities(select_entities)


class WolfSwitch(WolfEntity, SwitchEntity):
    """Implementation of Wolf Select entity for mode selections"""

    @property
    def is_on(self) -> bool | None:
        """Return state of switch"""
        _state = self._ism8.read_sensor(self.dp_nbr)
        _LOGGER.debug(f"current_option from ISM: {_state}")
        return STATE_UNKNOWN if _state is None else _state

    async def async_turn_on(self):
        """Change the selected option."""
        _LOGGER.debug(f"send dp {self.dp_nbr}: 1")
        self._ism8.send_dp_value(self.dp_nbr, 1)
        self.async_write_ha_state()

    async def async_turn_off(self):
        """Change the selected option."""
        _LOGGER.debug(f"send dp {self.dp_nbr}: 0")
        self._ism8.send_dp_value(self.dp_nbr, 0)
        self.async_write_ha_state()
