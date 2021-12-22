# Wolf Climate Control ISM8 for Home Assistant
An integration of WOLF's Heating ISM8 module into Home Assistant.

Supported devices:
  - HG(1-4) ("HeizGerät")
  - MM(1-3) ("MischerModul")
  - BM(1-4) ("BedienModul")
  - SM ("SolarModul")
  - KM ("KaskadenModul")
  - CWL ("Comfort WohnungsLüftung")
  
## INSTALLATION 
1. Download and place the integration files in the "custom_components" folder (it's located in the directory with your configuration files. Usually named ".homeassistant" in your home. If it doesn't exist there, create it):

    - .homeassistant/custom_components/wolf/binary_sensor.py
    - .homeassistant/custom_components/wolf/sensor.py
    - .homeassistant/custom_components/wolf/const.py
    - .homeassistant/custom_components/wolf/manifest.json
    - .homeassistant/custom_components/wolf/\_\_init\_\_.py

3. Add the integration in the configuration.yaml and specify the devices you own. The numbers are important if you have several identical modules, most commonly several BM's. If you only have 1 device, its number is .....1 ! Here the example configuration for 1 central heating (CGB2-14 in my case), with one integrated controller device and a solar module (there can be only one solar module, so no numbers):


    ```yaml7
     wolf:
       devices: 
         - HG1
         - BM1
         - SM
    ```

5. Be sure to have the ISM8 correctly configured with the IP adress of your machine running home-assistant. The standard Port-number in ISM8 is 12004, just leave it as is. If you wish to use a custom port, you have to use the "port"-configuration option (see below). Also, ISM8 needs to reboot(!) after any significant changes, so turn your heating device on/off after configuration.

6. Full Configuration settings, in an example with all options in place:

   ```yaml7
     wolf:
       devices:
         - HG1
       host:
         - 192.168.2.222
       port:
         - 12004
    ```

The host option lets you set an IP adress to listen ON, if your homeassistant server has several network adresses. The default port number of ISM8 is 12004, you can change it in the ISM8 GUI; in this case you will have to provide the custom port with the "port"-configuration option.

Enjoy. 

## SCREENSHOTS
<img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s1.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s2.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s3.PNG"> <img width="300" src="https://github.com/marcschmiedchen/home-assistant-wolf_ism8/blob/master/screenshots/s4.PNG">

## TODO

 - writing support for automation & control of the heating. Will definitely not be in the nearer future -- maybe never.
 - autodiscover device
 - ...
