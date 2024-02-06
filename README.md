# Wolf Climate Control ISM8 für Home Assistant
Eine Home Assistant Integration für das WOLF ISM8 Modul.

Kompatibel mit:
  - Heizgerät 1-4
  - direkter Heizkreis
  - Mischerkreis 1-3
  - Kaskadenmodul
  - Solarmodul
  - Comfort Wohnraumlüftung
  - Wärmepumpe
  - Systembedienmodul (BM2)
  
## INSTALLATION 

### Manuelle Version
1. Download und entpacken der Dateien in den Ordner"custom_components" im Konfigurationsverzeichnis von Home Assistant (Heißt meistens ".homeassistant" in Core, oder auch "config" im Docker Container. Wenn es noch nicht existiert, einfach erzeugen.)
2. Der "wolf"-Unterordner muss dort reinkopiert werden. 
3. Neustart von Home Assistant. Zuverlässiger ist das von Unix aus, aus der GUI habe ich manchmal das Gefühl, dass anklicken von "Neustart" nicht ausreicht. 
4. Unter Einstellungen -> Geräte&Dienste -> "Integration zufügen" wählen, nach Wolf suchen und installieren.

### Installation über HACS
1. Mittlerweile ist die Integration im HACS Store auffindbar. Einfach nach Wolf suchen, anklicken und so downloaden.
2. Nach dem Download neu starten(!). Danach kann die Integration wieder unter Einstellungen -> Geräte&Dienste -> "Integration zufügen" installiert werden. 


Wichtig ist hier ganz besonders: Neustart hilft bei vielen Problemen während/nach der Installation. 

### Weitere Schritte & Konfiguration
1. (optional): Angabe der IP Adresse und des Ports, auf dem die Integration am Netzwerk lauscht. Das ist NICHT die Adresse des ISM8-Moduls, sondern die HA-Server IP-Adresse, die mit dem ISM8 kommunizieren soll. Die Standardeinstellung "0.0.0.0" lauscht auf allen verfügbaren Netzwerkkarten und sollte fast immer OK sein. 12004 ist der Standard-Port, mit dem das ISM8 geliefert wird, und das sollte eigentlich auch fast immer OK sein.
2. Die IP-Adresse eurer HA-Instanz und die Portnummer muss im ISM8 hinterlegt sein. Achtung, das ISM8 muss neu booten, wenn man die Einstellungen ändert.
3. Im letzten Schritt alle Geräte auswählen, die ihr besitzt oder angezeigt bekommen wollt. Wenn ihr mehr auswählt, ist das zwar nicht schlimm, aber es werden dann ungenutzte Entitäten in HA angelegt, die nie einen Wert bekommen. 
4. Es gibt einen Punkt "undokumentierte Daten" --> manchmal kommen Daten vom ISM8, die in der Doku (noch nicht) hinterlegt ist. Damit sie nicht verloren gehen oder Fehler auslösen, habe ich sie hierhin verschoben. Wenn jemand rausfindet was das ist, integriere ich sie gern.

## SCREENSHOTS
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s1.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s2.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s3.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s4.PNG">

## TODO

 - Integration von Pull auf Push umstellen
 - ggf. Autodiscover 