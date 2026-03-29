"""Provide info for system health."""

from typing import Any

from homeassistant.components.system_health import SystemHealthRegistration
from homeassistant.core import HomeAssistant
from homeassistant.core import callback

from .const import DOMAIN


@callback
def async_register(hass: HomeAssistant, register: SystemHealthRegistration) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get info for the info page."""
    data = {}

    for entry in hass.config_entries.async_entries(DOMAIN):
        # We use runtime_data if available, otherwise fallback or skip
        if not hasattr(entry, "runtime_data"):
            continue

        wolf_data = entry.runtime_data
        if wolf_data.protocol.connected():
            ip_address = wolf_data.protocol.get_remote_ip_adress()
            data["Connection"] = f"Connected to {ip_address}"
            if hasattr(wolf_data, "sw_version"):
                data["SW Version"] = wolf_data.sw_version
            if hasattr(wolf_data, "hw_version"):
                data["HW Version"] = wolf_data.hw_version
            if hasattr(wolf_data, "serial_number"):
                data["Serial Number"] = wolf_data.serial_number
        else:
            data["Connection"] = "Disconnected"
    return data
