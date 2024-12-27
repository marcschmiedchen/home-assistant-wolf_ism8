"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_DEVICES, STATE_UNKNOWN
from wolf_ism8 import Ism8
from .wolf_entity import WolfEntity
from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    performs setup of the <select> entities
    """
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]
    ism8_fw = hass.data[DOMAIN]["sw_version"]

    select_entities = []
    for nbr in ism8.get_all_sensors().keys():
        dp_name = ism8.get_name(nbr)

        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        if not ism8.is_writable(nbr):
            continue
        # those are DPT_SWITCH, but trigger (button-)entities
        if nbr in (193, 194):
            continue

        if ism8.get_type(nbr) not in (
            SENSOR_TYPES.DPT_HVACMODE,
            SENSOR_TYPES.DPT_HVACMODE_CWL,
            SENSOR_TYPES.DPT_DHWMODE,
            SENSOR_TYPES.DPT_SWITCH,
        ):
            continue

        if ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"DP {nbr} not supported by firmware")
            continue

        # check if datapoint is on of the "Program"-Triples.
        # in this case, only the first entry is instantiated as a
        # WolfSelect-Entity with custom range from 1..3, the other two
        # datapoint-entries do not create a sensor instance
        if dp_name[-2:] in (" 1", " 2", " 3"):
            if dp_name[-2:] == " 1":
                _LOGGER.debug("initializing <Programm> Entity: %s", dp_name)
                select_entities.append(WolfProgrammSelect(ism8, nbr))
        else:
            _LOGGER.debug("initializing <Select> entity: %s", dp_name)
            select_entities.append(WolfSelect(ism8, nbr))

    async_add_entities(select_entities)


class WolfSelect(WolfEntity, SelectEntity):
    """Implementation of Wolf Select entity for mode selections"""

    @property
    def options(self):
        """Return all available options"""
        _options = []
        if self._type in (
            SENSOR_TYPES.DPT_HVACMODE,
            SENSOR_TYPES.DPT_DHWMODE,
            SENSOR_TYPES.DPT_SWITCH,
        ):
            for opt in self._value_range:
                _options.append(str(opt))
        return _options

    @property
    def state(self) -> str | None:
        """Return the entity state."""
        return self.current_option

    @property
    def current_option(self):
        """Return state of selection"""
        _prog = str(self._ism8.read_sensor(self.dp_nbr))
        return STATE_UNKNOWN if _prog is None else _prog

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self._type == SENSOR_TYPES.DPT_SWITCH:
            option = int(option)
        _LOGGER.debug(f"send dp {self.dp_nbr}: {type(option)} {option}")
        self._ism8.send_dp_value(self.dp_nbr, option)


class WolfProgrammSelect(WolfEntity, SelectEntity):
    """Implementation of Wolf Select entity for program-selections"""

    @property
    def options(self):
        """Return all available options"""
        return ["1", "2", "3"]

    # take away the last two chars from "zeitprogramm options-name
    @property
    def name(self) -> str:
        """Return the name of this entity."""
        return self._name[:-2]

    @property
    def current_option(self):
        """Return state of selection"""
        _prog = STATE_UNKNOWN
        if self._ism8.read_sensor(self.dp_nbr) == 1:
            _prog = "1"
        elif self._ism8.read_sensor(self.dp_nbr + 1) == 1:
            _prog = "2"
        elif self._ism8.read_sensor(self.dp_nbr + 2) == 1:
            _prog = "3"
        return _prog

    @property
    def state(self) -> str | None:
        """Return the entity state."""
        return self.current_option

    async def async_added_to_hass(self) -> None:
        """Register callbacks for all 3 datapoints which may affect this entity."""
        self._ism8.register_callback(self.async_write_ha_state, self.dp_nbr)
        self._ism8.register_callback(self.async_write_ha_state, self.dp_nbr + 1)
        self._ism8.register_callback(self.async_write_ha_state, self.dp_nbr + 2)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug(f"send dp {self.dp_nbr}: int {int(option) - 1}")
        self._ism8.send_dp_value(self.dp_nbr + (int(option) - 1), 1)
        self._attr_current_option = option
        self._state = option
