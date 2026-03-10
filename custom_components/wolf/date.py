import logging

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    performs setup of the data entities, needs a
    reference to an ism8-protocol implementation via config_entry.runtime_data
    """
    ism8 = config_entry.runtime_data.protocol
    ism8_fw = config_entry.runtime_data.sw_version

    date_entities = []
    for nbr in ism8.get_all_sensors().keys():
        # only add sensors which were enabled in the config
        if ism8.get_device(nbr) not in config_entry.data[CONF_DEVICES]:
            continue
        # only add sensors which are writable
        if not ism8.is_writable(nbr):
            continue
        if ism8.get_type(nbr) != SensorType.DPT_DATE:
            continue
        if (ism8_fw is not None) and ism8.first_fw_version(nbr) > ism8_fw:
            _LOGGER.debug(f"sensor {nbr} not supported by firmware")
            continue
        date_entities.append(WolfDate(ism8, nbr))

    async_add_entities(date_entities)


class WolfDate(WolfEntity, DateEntity):
    """
    Date Entity for ISM8 datapoints which can be written to
    """

    @property
    def native_value(self):
        """Return the state of the device."""
        return self._ism8.read_sensor(self.dp_nbr)

    async def async_set_value(self, date) -> None:
        """Update the current value."""
        _LOGGER.debug(f"send dp {self.dp_nbr}: {date}")
        self._ism8.send_dp_value(self.dp_nbr, date)
