# TODO: Wolf ISM8 Integration Improvements

This list outlines deviations from Home Assistant best practices and suggestions for architectural improvements.

## Core & Architecture
- [x] **Modernize Entry Data:** Transition from `hass.data[DOMAIN]` to `config_entry.runtime_data` (introduced in HA 2024.1).
- [x] **Set device info during init:** set most device info once when website scraping finishes, instead of in every entity.
- [x] **Shared ClientSession:** Replace manual `aiohttp.ClientSession()` in `__init__.py` with `async_get_clientsession(hass)`.
- [x] **Connection Management:** Refactor the 20-second `asyncio.sleep` loop in `async_setup_entry`. Entities should handle availability dynamically.
- [ ] **HTML Scraping:** Move firmware version scraping logic from `__init__.py` to a more appropriate location (ideally the `wolf_ism8` library or a dedicated helper).
- [ ] **Diagnostics:** Implement `diagnostics.py` to provide redacted info for troubleshooting.
- [x] **System Health:** Implement `system_health.py` to show connection status in HA.
- [x] **Performance:** set static data without the use of properties. Use the attr_ variables directly.

## Entities & Platforms
- [ ] **Translations:** Add entity-level translation keys in `translations/*.json` to support localized entity names and states.
- [x] **Type Hints:** Add missing type hints to function signatures, particularly in `async_setup_entry` across platform files.
- [ ] **Hardcoded Logic:** Refactor `device_class` and `icon` logic that currently relies on string matching of entity names. Use fixed identifiers or `EntityDescription`.
- [ ] **Hardcoded Units:** Replace hardcoded units (e.g., "l/h") with HA constants or standardized strings where applicable.
- [ ] **Button IDs:** Refactor hardcoded DP numbers (193, 194) in `button.py` into constants.

## Quality & Maintenance
- [x] **Logging:** Replace any remaining `print()` statements with `_LOGGER`.
- [ ] **Testing:** Implement unit and integration tests (none currently exist).
- [x] **Cleanup:** Remove manual `pop` logic in `async_unload_entry` once `runtime_data` is implemented.
