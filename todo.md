# Todo List - Home Assistant Wolf Integration Improvements

This document lists identified inconsistencies, naming issues, redundant code, and possible improvements for the `wolf` integration.

## 🔴 Critical Issues
- [x] **Missing `asyncio` import**: In `custom_components/wolf/__init__.py`, `asyncio.timeout` and `asyncio.sleep` are used. Fixed by adding the import.
- [x] **Incorrect variable reference**: `custom_components/wolf/system_health.py` now uses `wolf_data.serial_number` instead of the outdated `serno`.

## 🧹 Naming & Consistency
- [x] **Class Naming**: Rename `WolfProgrammSelect` to `WolfProgramSelect` in `custom_components/wolf/select.py`. Fixed.
- [x] **Property Naming**: `@property available` in `WolfEntity` is used consistently. Fixed.
- [x] **Config Flow Naming**: `WolfCustomConfigFlow` was renamed to `WolfConfigFlow`. Fixed.
- [x] **Data Classes**: `serial_number` is used instead of `serno` consistently across the project. Fixed.

## ⚙️ Code Quality & Performance
- [ ] **Scraping Logic**: The `while not ism8.connected(): await asyncio.sleep(5)` loop in `__init__.py` could be improved to use an event-driven approach if the `wolf_ism8` library supports it.
- [x] **Type Hinting**:
    - Improve type hints for `WolfData` attributes. Fixed.
    - Add missing type hints for function parameters. Fixed.
    - `current_option` in `select.py` returns `str | None`. Fixed.
- [x] **Redundant Code**:
    - Remove `return` at the end of `get_webportal_info`. Fixed.
    - Remove redundant `asyncio.iscoroutine(result)` check in `async_unload_entry`. Fixed.

## 🧪 Testing
- [ ] **Add Tests**: The project currently lacks a `tests/` directory. Implement unit and integration tests to verify setup, config flow, and entity behavior.
