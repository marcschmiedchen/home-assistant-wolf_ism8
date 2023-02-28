# Wolf Climate Control ISM8 for Home Assistant
An integration of WOLF's Heating ISM8 module into Home Assistant.

Supported devices:
  - HG(1-4) ("HeizGerät")
  - MM(1-3) ("MischerModul")
  - DKW(1) ("Direkter Heizkreis/WW")
  - MK(1-3) ("MischerKreis")
  - SM ("SolarModul")
  - KM ("KaskadenModul")
  - CWL ("Comfort WohnungsLüftung")
  - BWL ("Luft-Wärmepumpe BWL")
  
## INSTALLATION 
Current Versions should be discoverable and use the GUI for configuration:

1. Enter the IP adress the integration should LISTEN on, which is the IP adress of the home assistant server. Alternatively you can leave the default 0.0.0.0, which listens on all available IP adresses. [By the way: the same adress must obviously be entered in the ISM8 web-configuration. Careful: ISM8 needs a reboot before changes are accepted]

2. Enter the port number the integration should LISTEN on. Standard value for ISM8 is 12004. However, if you change that in the config, you have to provide the port-number to the integration. Careful: ISM8 needs a reboot before changes are accepted.



## SCREENSHOTS
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s1.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s2.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s3.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s4.PNG">

## TODO

 - make integration async (local push)
 - autodiscover 
