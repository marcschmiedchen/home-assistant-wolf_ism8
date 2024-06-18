# Wolf Climate Control ISM8 for Home Assistant
An integration of WOLF's Heating ISM8 module into Home Assistant.

Supported devices (in German):
  - Heizgerät 1-4
  - direkter Heizkreis
  - Mischerkreis 1-3
  - Kaskadenmodul
  - Solarmodul
  - Comfort Wohnraumlüftung
  - Wärmepumpe
  - Systembedienmodul (BM2)
  
## INSTALLATION 
Current Versions use the GUI for Home assistant config-workflow for configuration.

### Manual Installation

1. - Download and place the integration files in the "custom_components" folder (it's located in the directory with your configuration files. Usually named ".homeassistant" in your home. If it doesn't exist there, create it). Place the "wolf"-folder into the custom-components directory:  
  .homeassistant/custom_components/wolf   
   - Alternatively, the integration should be available by using [HACS](https://hacs.xyz/), the Home Assistant Community Store.   
2. Enter the IP adress the integration should LISTEN on, which is the IP adress of the home assistant server. Alternatively you can leave the default 0.0.0.0, which listens on all available IP adresses. [By the way: the same adress must obviously be entered in the ISM8 web-configuration. Careful: ISM8 needs a reboot before changes are accepted]

3. Enter the port number the integration should LISTEN on. Standard value for ISM8 is 12004. However, if you change that in the config, you have to provide the port-number to the integration. Careful: ISM8 needs a reboot before changes are accepted.

4. Select the devices you have installed in your HVAC system. Datapoints from those devices are automatically added to HA, but only populated if the device is really on your network. So no harm in selecting more than you have, but it generates unneccesary entities in HA. Unfortunately you cannot tune this setting later on; in order to change the installed devices you would have to complete delete/reboot Server/reinstall the integration.

### Installation via HACS
1. The integration can be installed via the HACS Store. To do this, a "custom repository" must be added using the top right menu with the three dots. The link to the Github repo is entered here once ([https://github.com/marcschmiedchen/home-assistant-wolf_ism8]). Afterwards it always remains visible in your own HACS installation.
2. You can then select and install it. However, this process only downloads the integration. You'll still have to install it in the next step.
3. After downloading, be sure to restart(!).
4. After that, the integration can finally be installed under Settings -> Devices & Services -> "Add integration".

What is particularly important here is that restarting helps with many problems during/after installation


## SCREENSHOTS
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s1.PNG">
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s2.PNG">
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s3.PNG">
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s4.PNG">

## TODO
 - autodiscover 
