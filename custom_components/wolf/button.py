"""
Support for Wolf heating via ISM8 adapter
"""

import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .wolf_entity import WolfEntity
from .const import DOMAIN
from . import WolfData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[WolfData],
    async_add_entities,
):
    """performs setup of the button entities"""

    wolf_data = config_entry.runtime_data
    ism8 = wolf_data.protocol

    buttons = []
    for nbr in (193, 194):
        if ism8.get_device(nbr) in config_entry.data[CONF_DEVICES]:
            buttons.append(WolfButton(ism8, nbr))

    buttons.append(WolfRequestDataButton(ism8))
    async_add_entities(buttons)


class WolfButton(WolfEntity, ButtonEntity):
    """
    Button representation for ISM8 datapoints which can
    be triggered to start certain processes on ISM8
    """

    _attr_available = True

    def __init__(self, ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)
        if self.dp_nbr == 194:
            self._attr_icon = "mdi:hot-tub"
        else:
            self._attr_icon = "mdi:gesture-tap-button"

    async def async_press(self) -> None:
        """Handle the button press."""
        self._ism8.send_dp_value(self.dp_nbr, 1)


class WolfRequestDataButton(ButtonEntity):
    """
    Button to request all data-points from ISM8.
    This entity is not connected to any WOLF datapoints, nor callback functionality,
    so it should not inherit from class "WolfEntity"
    """

    _attr_has_entity_name = True
    _attr_unique_id = "999"
    _attr_icon = "mdi:update"
    _attr_available = True

    def __init__(self, ism8) -> None:
        self._ism8 = ism8
        self._device = "Systembedienmodul"
        self._attr_name = "Datenanforderung"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._device)},
        }
        _LOGGER.debug("setup wolf RequestDataButton")

    async def async_press(self) -> None:
        """Handle the button press."""
        self._ism8.request_all_datapoints()
