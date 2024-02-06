3.0.1 (2024-02-05)
------------------

New
~~~
- ignoring datapoints with unrealistic values (>1000°C, >1000m3/h)

Fixes
~~~~~~~
- fixed problem with "Programm" Selects
- several fixes in the wolf-api-library (on pypi: caching issues, conversion errors)

3.0 (2024-01-18)
------------------

New
~~~
- added/tested support for writing float datapoints to ISM8
- added undocumented datapoints instead of ignoring them
- added writable datapoints as "number" entities (feature request)


Changes
~~~~~~~
- updated config workflow
- breaking change: renamed all devices to full name instead of abbreviation (feature request)


Fixes
~~~~~~~
- catch "invalid data" from ISM8 and ignore it
- fixed update isses with select entities


x.x.x
------------------

New
~~~
- Everything
- started changelog at 3.0 (sorry)
