# Project Context: Home Assistant Integration
This project is a custom integration for Home Assistant. All code must adhere to the official Home Assistant Core architectural styles.

## Technical Guidelines (Mandatory)
* **Asynchronous Programming:** Always use `asyncio`. Avoid any blocking I/O. 
* **Communication:** Use `aiohttp` for all HTTP requests. 
* **Config Flow:** Configuration must happen via `config_flow.py`. Do not use `setup_platform` for manual YAML config.
* **Typing:** Use Python type hints (PEP 484) everywhere. Use `HomeAssistant` and `ConfigEntry` types from `homeassistant.core` and `homeassistant.config_entries`.

## Project Structure
- `custom_components/wolf/`: Main code
- `translations/`: JSON files for UI strings

## Common Patterns
- **Logging:** Use `_LOGGER = logging.getLogger(__name__)`.
- **Strings:** All user-facing strings must be in `de.json` (and other languages) and referenced via `translation_key`.
