# Wolf Climate Control ISM8 for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
![HASS Build](https://github.com/marcschmiedchen/home-assistant-wolf_ism8/workflows/hassfest/badge.svg)
![HASS Build](https://github.com/marcschmiedchen/home-assistant-wolf_ism8/workflows/hacs/badge.svg)

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English

An integration of WOLF's Heating ISM8 module into Home Assistant. The integration provides up to 300 datapoints which are delivered by the ISM8 via network. Some of them may be written to.

### Supported devices:
  - Heating Unit 1-4 (TOB, CGB-2, MGK-2, COB-2, TGB-2)
  - Direct heating circuit
  - Mixed heating circuit 1-3
  - Cascading module
  - Solar module SM
  - Ventilation (CWL Excellent, CWL 2)
  - Heatpump 1-4 (BWL1S, CHA)
  - Controller (BM2)

### Installation via HACS (Recommended)
1. In Home Assistant, go to HACS -> Integrations.
2. Click the three dots in the top right and select "Custom repositories".
3. Add `https://github.com/marcschmiedchen/home-assistant-wolf_ism8` and select category "Integration".
4. Search for "Wolf Climate Control ISM8" and install.
5. **Restart Home Assistant.**
6. Go to Settings -> Devices & Services -> Add Integration -> Search for "Wolf".

### Configuration
1. **IP/Port:** Enter the IP address and port of your Home Assistant server that the integration should listen on (Default: `0.0.0.0` (listens on all addresses) and `12004`). This must match the settings in your ISM8 web configuration.
2. **Devices:** Select the devices installed in your HVAC system.

---

<a name="deutsch"></a>
## Deutsch

Eine Home Assistant Integration für das WOLF ISM8 Modul. Die Integration stellt bis zu ca. 300 Datenpunkte zur Verfügung, die das ISM8 Modul über das Netzwerk liefert. Einige davon können auch beschrieben werden.

### Unterstützte Bereiche/Geräte:
  - Heizgerät 1-4 (TOB, CGB-2, MGK-2, COB-2, TGB-2)
  - direkter Heizkreis
  - Mischerkreis 1-3
  - Kaskadenmodul
  - Solarmodul
  - Comfort Wohnraumlüftung (CWL Excellent, CWL 2)
  - Wärmepumpe 1-4 (BWL1S, CHA)
  - Systembedienmodul (BM2)

### Installation über HACS
1. In Home Assistant zu HACS -> Integrationen navigieren.
2. Oben rechts auf die drei Punkte klicken -> "Benutzerdefinierte Repositories".
3. Link `https://github.com/marcschmiedchen/home-assistant-wolf_ism8` hinzufügen, Kategorie "Integration".
4. Nach "Wolf Climate Control ISM8" suchen und installieren.
5. **Home Assistant neu starten.**
6. Unter Einstellungen -> Geräte & Dienste -> Integration hinzufügen nach "Wolf" suchen.

### Konfiguration
1. **IP/Port:** IP-Adresse und Port des HA-Servers angeben, auf dem die Integration lauscht (Standard: `0.0.0.0` (wartet auf allen verfügbaren IP adressen) und `12004`). Diese Werte müssen im ISM8 hinterlegt sein.
2. **Geräte:** Wählen alle vorhandenen Geräte des Heizungssystems Systems aus. Andere Geräte werden dann nicht angelegt.

---

## Screenshots
<p align="center">
  <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/raw/master/screenshots/s1.PNG">
  <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/raw/master/screenshots/s2.PNG">
  <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/raw/master/screenshots/s3.PNG">
  <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/raw/master/screenshots/s5.PNG">
</p>
