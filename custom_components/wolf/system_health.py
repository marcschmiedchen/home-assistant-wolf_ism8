"""Provide info for system health."""
from typing import Any

from homeassistant.components.system_health import SystemHealthRegistration
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_register_system_health(
    hass: HomeAssistant, register: SystemHealthRegistration
) -> None:
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
        status = "Connected" if wolf_data.protocol.connected() else "Disconnected"
        data[f"Connection ({entry.title})"] = status
        
    return data
