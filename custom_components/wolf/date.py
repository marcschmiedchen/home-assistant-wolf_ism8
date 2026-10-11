import logging

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SensorType
from .wolf_entity import WolfEntity
from .wolf_entity import wolf_datapoint_matches_platform

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    performs setup of the data entities, needs a
    reference to an ism8-protocol implementation via config_entry.runtime_data
    """
    ism8 = config_entry.runtime_data.protocol

    date_entities = []
    for nbr in ism8.get_all_sensors().keys():
        # check if this sensor should be added to THIS platform
        if not wolf_datapoint_matches_platform(
            nbr,
            config_entry=config_entry,
            platforms=(SensorType.DPT_DATE,),
            writable=True,
        ):
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
        self.async_write_ha_state()
