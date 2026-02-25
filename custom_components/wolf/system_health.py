"""Provide info for system health."""

from typing import Any

from homeassistant.components.system_health import SystemHealthRegistration
from homeassistant.core import HomeAssistant, callback

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
            status_string = f"Connected to {wolf_data.ism8_ip_address}"
            data["Connection"] = status_string
            data["SW Version"] = wolf_data.sw_version
            data["HW Version"] = wolf_data.hw_version
            data["Serial Number"] = wolf_data.serno
        else:
            data["Connection"] = "Disconnected"
    return data
