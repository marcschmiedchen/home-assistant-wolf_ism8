import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .wolf_entity import WolfEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """performs setup of the button entities"""

    ism8 = config_entry.runtime_data.protocol

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

    def __init__(self, ism8, dp_nbr: int) -> None:
        super().__init__(ism8, dp_nbr)
        match self.dp_nbr:
            case 194:
                self._attr_icon = "mdi:hot-tub"
            case _:
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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device)},
            name=self._device,
        )
        _LOGGER.debug("setup wolf RequestDataButton")

    async def async_press(self) -> None:
        """Handle the button press."""
        self._ism8.request_all_datapoints()
