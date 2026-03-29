"""Config flow for Wolf SmartSet Service integration."""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICES
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PORT
from wolf_ism8 import Ism8

from .const import DEFAULT_HOST
from .const import DEFAULT_PORT
from .const import DOMAIN
from .const import WOLF_DEFAULT_DEVICES

WOLF_HOST_SCHEMA = {
    vol.Required(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
}

WOLF_DEVICE_SCHEMA = {}
for _device in Ism8.get_all_devices():
    device_is_default = _device in WOLF_DEFAULT_DEVICES
    WOLF_DEVICE_SCHEMA[vol.Optional(_device, default=device_is_default)] = cv.boolean


class WolfConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """wolf config flow"""

    def __init__(self) -> None:
        """Initialize with empty host and port."""
        self.host = None
        self.port = None
        self.devices = None

    async def async_step_user(self, user_input=None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            self.host = user_input[CONF_HOST]
            self.port = user_input[CONF_PORT]

            return await self.async_step_device()

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(WOLF_HOST_SCHEMA), errors=errors
        )

    async def async_step_device(self, user_input=None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.devices = []
            for _device in Ism8.get_all_devices():
                if user_input[_device]:
                    self.devices.append(_device)

            data = {
                CONF_HOST: self.host,
                CONF_PORT: self.port,
                CONF_DEVICES: self.devices,
            }

            return self.async_create_entry(title="WOLF ISM8 Adapter", data=data)

        return self.async_show_form(
            step_id="device", data_schema=vol.Schema(WOLF_DEVICE_SCHEMA), errors=errors
        )
