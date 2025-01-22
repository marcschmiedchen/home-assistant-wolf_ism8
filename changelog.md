# Changelog
## 4.1 (2025-01-22)
### Fixed
- unloading integration / freeing network resources on unload (issue #71)
- fixed re-entry into config leading to setup errors (issue #70)
- switched to latest wolf library with more restrictive logging

## 4.0 (2024-12-29)
### Added
- added support for statistics
- scraping web portal for information on firmware of ISM8
- [breaking] suppressing datapoints which are not supported in ISM8 FW-version
- added support for up to 4 heatpumps (Waermepumpe 1-4)
- [breaking] switched to latest wolf library with support for specific modes for CHA 
- added support for solar "active energy" (Gesamtertrag) sensor
- link to ISM webportal now available in device-card

## 3.3.1 (2024-10-07)
### Fixed
- update of binary sensor would not come through
### Added
- support for unloading integration from GUI. Freeing network resources.

## 3.3 (2024-10-04)
### Fixed
- entity state is not longer directly set, usind native_value instead.
- this enables HA unit conversion and precision adjustment

## 3.2.5 (2024-09-14)
### Fixed
- fixed await-issue during init

## 3.2.4 (2024-07-03)
### Fixed
- bumped library version

## 3.2.3 (2024-07-03)
### Fixed
- fixed bug with time entity
- switched to enum.StrEnum for compatibility

## 3.2.2 (2024-06-30)
### Fixed
- fixed bug with date entity

## 3.2.1 (2024-06-23)
### Fixed
- small bug with naming convention for button "Datenanforderung"

## 3.2 (2024-06-05)
### Changed
- changed data service type from "polling" to "push" via callback

## 3.1 (2024-06-05)
### Added
- added support for date and time entries for CWL

## 3.0.2 (2024-04-05)
### Added
- added support for HVACCONTRMODE-Sensor

## 3.0.1 (2024-02-05)
### Added
- ignoring datapoints with unrealistic values (>1000°C, >1000m3/h)
### Fixed
- fixed problem with "Programm" Selects
- several fixes in the wolf-api-library (on pypi: caching issues, conversion errors)

## 3.0 (2024-01-18)
### Added
- added/tested support for writing float datapoints to ISM8
- added undocumented datapoints instead of ignoring them
- added writable datapoints as "number" entities (feature request)
### Changed
- updated config workflow
- **Breaking:**: renamed all devices to full name instead of abbreviation (feature request)
### Fixed
- catch "invalid data" from ISM8 and ignore it
- fixed update isses with select entities


## 1.0.0 (2020)
### Added
- Everything
- Started changelog at 3.0 (sorry)
