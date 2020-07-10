# homeassistant-wolf-ism8
An integration of from Wolf's Heating ISM8 module into Home Assistant.

Supported devices:
  - HG(1-4) ("HeizGerät")
  - MM(1-3) ("MischerModul")
  - BM(1-4) ("BedienModul")
  - SM ("SolarModul")
  - KM ("KaskadenModul")
  - CWL ("Comfort WohnungsLüftung")
  
  
### INSTALLATION
1. Have Home-Assistant readily installed

2. Download and place the integration files in the "custom_components" folder (it's located in the directory with your configuration files. Usually named ".homesassistant". If it doesn't exist there, create it):

    - .homeassistant/custom_components/wolf/binary_sensor.py
    - .homeassistant/custom_components/wolf/sensor.py
    - .homeassistant/custom_components/wolf/\_\_init\_\_.py

3. Add the integration in the configuration.yaml and specify the devices you own. The numbers are important if you have several identical modules, most commonly several BM's. If you only have 1 device, its number is .....1 ! Here the example configuration for 1 central heating (CGB2-14 in my case), with one integrated controller device and a solar module (there can be only one solar module, so no numbers)


    ```yaml7
     wolf:
       devices: 
         - HG1
         - BM1
         - SM
    ```

5. Be sure to have the ISM8 correctly configured with the IP adress of your machine running home-assistant. Also ISM8 needs to reboot after significant changes, so turn your heating device on/off after configuration.

6. The sensors will be populated by the ISM8 over some time, since they only are updated when relevant changes occur. Enjoy. 



### TODO

 - writing support for automation & control of the heating. Will definitely not be in the nearer future -- maybe never.
 - autodiscover device
 - ...
