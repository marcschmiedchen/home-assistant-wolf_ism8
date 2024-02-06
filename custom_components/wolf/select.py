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

    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]

    select_entities = []
    for nbr in ism8.get_all_sensors().keys():
        wolf_device = ism8.get_device(nbr)
        wolf_name = ism8.get_name(nbr)
        wolf_type = ism8.get_type(nbr)

        if wolf_device not in config[CONF_DEVICES]:
            continue
        if not ism8.is_writable(nbr):
            continue
        # those are DPT_SWITCH, but trigger (button-)entities
        if nbr in (193, 194):
            continue

        # check if datapoint is on of the "Program"-Triples.
        # in this case, only the first entry is instantiated as a
        # WolfSelect-Entity with custom range from 1..3, the other two
        # datapoint-entries do not create a sensor instance
        if wolf_name[-2:] in (" 1", " 2", " 3"):
            if wolf_name[-2:] == " 1":
                # _LOGGER.debug("found <Programm> Entity: %s", wolf_name)
                select_entities.append(WolfProgrammSelect(ism8, nbr))
        elif wolf_type in (
            SENSOR_TYPES.DPT_HVACCONTRMODE,
            SENSOR_TYPES.DPT_HVACMODE,
            SENSOR_TYPES.DPT_DHWMODE,
            SENSOR_TYPES.DPT_SWITCH,
        ):
            select_entities.append(WolfSelect(ism8, nbr))

    async_add_entities(select_entities)


class WolfSelect(WolfEntity, SelectEntity):
    """Implementation of Wolf Select entity for mode selections"""

    _attr_current_option = STATE_UNKNOWN

    @property
    def options(self):
        """Return all available options"""
        _options = []
        if self._type in (
            SENSOR_TYPES.DPT_HVACCONTRMODE,
            SENSOR_TYPES.DPT_HVACMODE,
            SENSOR_TYPES.DPT_DHWMODE,
            SENSOR_TYPES.DPT_SWITCH,
        ):
            for opt in self._value_range:
                _options.append(str(opt))
        return _options

    async def async_update(self) -> None:
        """Return state"""
        self._attr_current_option = str(self._ism8.read_sensor(self.dp_nbr))
        if self._attr_current_option is None:
            self._attr_current_option = STATE_UNKNOWN
        self._state = self._attr_current_option
        return

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self._type == SENSOR_TYPES.DPT_SWITCH:
            option = int(option)
        _LOGGER.debug(f"send dp {self.dp_nbr}: {type(option)} {option}")
        self._ism8.send_dp_value(self.dp_nbr, option)


class WolfProgrammSelect(WolfEntity, SelectEntity):
    """Implementation of Wolf Select entity for program-selections"""

    _attr_current_option = STATE_UNKNOWN

    @property
    def options(self):
        """Return all available options"""
        return ["1", "2", "3"]

    # take away the last two chars from "zeitprogramm options-name
    @property
    def name(self) -> str:
        """Return the name of this entity."""
        return self._name[:-2]

    async def async_update(self) -> None:
        """Return state"""
        _prog = STATE_UNKNOWN
        if self._ism8.read_sensor(self.dp_nbr) == 1:
            _prog = "1"
        elif self._ism8.read_sensor(self.dp_nbr + 1) == 1:
            _prog = "2"
        elif self._ism8.read_sensor(self.dp_nbr + 2) == 1:
            _prog = "3"
        self._attr_current_option = _prog
        self._state = _prog
        return

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._ism8.send_dp_value(self.dp_nbr + (int(option) - 1), 1)
        self._attr_current_option = option
        self._state = option
