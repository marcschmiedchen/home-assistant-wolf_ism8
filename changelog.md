# Changelog
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
