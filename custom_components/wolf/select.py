"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_DEVICES
from wolf_ism8 import Ism8
from .const import (
    DOMAIN,
    WOLF,
    WOLF_ISM8,
    SensorType,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
):
    """
    performs setup of the <select> entities, expects a
    reference to an ism8-adapter via hass.data
    """

    config = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("%s", config[CONF_DEVICES])
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
        # (those are button-entities)
        if nbr in (193, 194):
            continue

        _LOGGER.debug("start processing select-entity %s: %s", nbr, wolf_name)
        # check if datapoint is on of the "Program"-Triples.
        # in this case, only the first entry is instantiated as a
        # WolfSelect-Entity with custom range from 1..3, the other two
        # datapoint-entries do not create a sensor instance
        if wolf_name[-2:] in (" 1", " 2", " 3"):
            if wolf_name[-2:] == " 1":
                _LOGGER.debug("found <Programm> Entity: %s", wolf_name)
                select_entities.append(WolfProgrammSelect(ism8, nbr))
            else:
                _LOGGER.debug("skipped %s; dp has been merged to first entry", nbr)
        elif wolf_type in (
            SensorType.DPT_HVACCONTRMODE,
            SensorType.DPT_HVACMODE,
            SensorType.DPT_DHWMODE,
            SensorType.DPT_TEMPD,
            SensorType.DPT_SWITCH,
        ):
            select_entities.append(WolfSelect(ism8, nbr))

    async_add_entities(select_entities)


class WolfSelect(SelectEntity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
    dp_nbr represents the unique identifier of the up to 200 different
    sensors
    """
    _attr_current_option = None

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        self.dp_nbr = dp_nbr
        self._device = ism8.get_device(dp_nbr)
        self._name = self._device + "_" + ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._option_ids = {}
        self._ism8: Ism8 = ism8
        _LOGGER.debug(
            "Setup <Select> Entity %s (id: %d, %s)",
            self._name,
            self.dp_nbr,
            self._type,
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
        return {
            "identifiers": {(DOMAIN, self._device)},
            "name": self._device,
            "manufacturer": WOLF,
            "model": WOLF_ISM8,
        }

    @property
    def options(self):
        """Return all available options"""

        _options = []
        if self._type in (SensorType.DPT_HVACCONTRMODE,
                          SensorType.DPT_HVACMODE,
                          SensorType.DPT_DHWMODE,
                          SensorType.DPT_TEMPD,
                          SensorType.DPT_SWITCH):
  
            for opt in self._ism8.get_value_area(self.dp_nbr):
                _options.append(str(opt))
        else:
            _LOGGER.error("Unknown datapoint type %s for select sensor", self._type)
        return _options

    async def async_update(self) -> None:
        """Return state"""
        self._attr_current_option = str(self._ism8.read(self.dp_nbr))
        return

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self._type == SensorType.DPT_TEMPD:
            option = float(option)
        _LOGGER.debug("sent value %s to ISM8 dp nbr: %s", option, self.dp_nbr)            
        self._ism8.send_dp_value(self.dp_nbr, option)


class WolfProgrammSelect(SelectEntity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
    dp_nbr represents the unique identifier of the up to 200 different
    sensors
    """
    _attr_current_option = None

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        self.dp_nbr = dp_nbr
        self._device = ism8.get_device(dp_nbr)
        self._name = self._device + "_" + ism8.get_name(dp_nbr)[:-2]
        self._type = ism8.get_type(dp_nbr)
        self._ism8: Ism8 = ism8
        _LOGGER.debug(
            "Setup select sensor %s (dd_id: %d) as %s",
            self._name,
            self.dp_nbr,
            self._type,
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

    @property
    def options(self):
        """Return all available options"""
        return ["1", "2", "3"]

    async def async_update(self) -> None:
        """Return state"""
        _prog = "1"
        if self._ism8.read(self.dp_nbr):
            _prog = "1"
        elif self._ism8.read(self.dp_nbr + 1):
            _prog = "2"
        elif self._ism8.read(self.dp_nbr + 2):
            _prog = "3"
        self._attr_current_option = _prog
        return

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug("sent value 1 to ISM8: %s", self.dp_nbr + (int(option) - 1))
        self._ism8.send_dp_value(self.dp_nbr + (int(option) - 1), 1)
