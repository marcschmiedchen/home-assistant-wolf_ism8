"""
Support for Wolf heating via ISM8 adapter
"""

from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_DEVICES
from wolf_ism8 import Ism8
from .wolf_entity import WolfEntity
from .const import DOMAIN, WOLF, WOLF_ISM8


async def async_setup_entry(hass, config_entry, async_add_entities):
    """performs setup of the button entities"""

    config = hass.data[DOMAIN][config_entry.entry_id]
    ism8: Ism8 = hass.data[DOMAIN]["protocol"]

    buttons = []
    for nbr in (193, 194):
        if ism8.get_device(nbr) in config[CONF_DEVICES]:
            buttons.append(WolfButton(ism8, nbr))

    buttons.append(WolfRequestDataButton(ism8))
    async_add_entities(buttons)


class WolfButton(WolfEntity, ButtonEntity):
    """
    Button representation for ISM8 datapoints which can
    be triggered to start certain processes on ISM8
    """

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
    Button to request all data-points from ISM8.
    This entity is not connected to any WOLF datapoints, nor callback functionality,
    so it should not inherit from class "WolfEntity"
    """

    def __init__(self, ism8: Ism8) -> None:
        self._ism8 = ism8
        self._library_version = ism8.get_library_version()

    @property
    def unique_id(self):
        """Return the unique_id of this sensor."""
        return "999"

    @property
    def icon(self):
        """Return icon"""
        return "mdi:update"

    @property
    def name(self) -> str:
        """Return the name of this entity."""
        return "Datenanforderung"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "Systembedienmodul")},
            "name": "Systembedienmodul",
            "manufacturer": WOLF,
            "model": WOLF_ISM8,
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        self._ism8.request_all_datapoints()
