## 🎯 Project Context
* **Target:** Home Assistant Custom Integration (Wolf GmbH Heating Systems).
* **Goal:** High-performance, push-based integration for HACS and eventual Core submission.
* **Architecture:** Callback-driven updates (No `DataUpdateCoordinator`).
* **Locale:** German hardware/logic

## 🚀 Performance & Footprint Philosophy
* **Push over Pull:** Zero-polling architecture. Library uses persistent async connections (WebSockets/TCP/UDP).
* **Minimal Overhead:** Avoid `DataUpdateCoordinator` boilerplate. Use direct state updates via `self.async_write_ha_state()`.
* **Small Footprint:** No unnecessary third-party wrappers. Use `aiohttp` and native Python `asyncio`.
* **Efficient State Management:** Entities subscribe to specific hardware data points to minimize internal bus traffic.

## 🛠 Technical Guidelines (Mandatory)
* **Async Everything:** Strictly `asyncio`. Absolutely no blocking I/O in the event loop.
* **Communication:** Use `async_get_clientsession` from `homeassistant.helpers.aiohttp_client`.
* **Config Flow:** Mandatory `config_flow.py`. No YAML configuration allowed.
* **Type Hinting:** PEP 484 type hints required for all methods.
    - Use `HomeAssistant` from `homeassistant.core`.
    - Use `ConfigEntry` from `homeassistant.config_entries`.
* **Standardization:** Follow PEP 8 and Home Assistant Core architectural styles.

## 📂 Project Structure
* `custom_components/wolf/`:
    * `__init__.py`: Entry setup, connection management, and teardown.
    * `const.py`: Shared constants (DOMAIN, brand names).
    * `config_flow.py`: UI-based setup and validation.
    * `entity.py`: Base `WolfEntity` class handling callback registration.
    * `sensor.py`, `climate.py`, `binary_sensor.py`: Platform-specific entities.
* `translations/`: JSON files for localized UI strings (ensure `en.json` exists).

## 📝 Coding Patterns
* **Logging:** Use `_LOGGER = logging.getLogger(__name__)`.
* **Unique IDs:** Must be derived from hardware serial numbers/MAC addresses.
* **Entity Naming:** Use the latest HA naming conventions (avoiding "Wolf" in the `name` attribute).
* **Cleanup:** Ensure `async_will_remove_from_hass` properly unregisters listeners to prevent memory leaks.

## 🤖 Interaction Rules
1. **No Coordinator:** Never suggest or use `DataUpdateCoordinator`. Use a central Data Manager/API class that accepts update listeners.
2. **Core Compliance:** Always prioritize "The Home Assistant Way" for entity properties and config flows.
3. **Clean Teardown:** Every proposed solution must include logic for a clean `async_unload_entry`.
