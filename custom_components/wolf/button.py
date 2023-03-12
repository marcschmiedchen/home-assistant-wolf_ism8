"""
Support for Wolf heating via ISM8 adapter
"""
import logging
from collections.abc import Callable
from homeassistant import config_entries
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_DEVICES
from homeassistant.helpers.typing import HomeAssistantType
from wolf_ism8 import Ism8
from .const import (
    DOMAIN,
    WOLF,
    WOLF_ISM8,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable,
):
    """
    performs setup of the button entities, needs a
    reference to an ism8-protocol implementation via hass.data
    """

    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]

    buttons = []
    for nbr in (193,194):
        if ism8.get_device(nbr) in config[CONF_DEVICES]:
                buttons.append(WolfButton(ism8, nbr))

    buttons.append(WolfRequestDataButton(ism8))
    async_add_entities(buttons)


class WolfButton(ButtonEntity):
    """
    Button representation for ISM8 datapoints which can
    be triggered to start certain processes on ISM8
    """

    def __init__(self, ism8: Ism8, dp_nbr: int) -> None:
        self.dp_nbr = dp_nbr
        self._device = ism8.get_device(dp_nbr)
        self._name = self._device+"_"+ism8.get_name(dp_nbr)
        self._type = ism8.get_type(dp_nbr)
        self._ism8 = ism8
        _LOGGER.debug("setup <button> no. %d as %s", self.dp_nbr, self._type)

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
    def icon(self):
        """Return icon"""
        if self.dp_nbr == 194:
            return "mdi:hot-tub"
        else:
            return "mdi:gesture-tap-button"

    async def async_press(self) -> None:
        """Handle the button press."""
        self._ism8.send_dp_value(self.dp_nbr, 1)

        
class WolfRequestDataButton(ButtonEntity):
    """
    Button to request all data-points from ISM8
    """

    def __init__(self, ism8: Ism8) -> None:
        self._device = 'SYM'
        self._name = 'SYM_request_data'
        self._ism8 = ism8
        _LOGGER.debug("setup <button> DataRequest")

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique_id of this sensor."""
        return "999"

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
    def icon(self):
        """Return icon"""
        return "mdi:update"
 
    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug('sending Datapoint Request to ISM8')
        self._ism8.request_all_datapoints()
