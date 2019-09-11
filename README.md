# Pycom

## Deployment Instructions

* Install Pycom's [**pymakr**](https://docs.pycom.io/gettingstarted/installation/pymakr/) plugin on Atom [**(instructions)**](https://docs.pycom.io/pymakr/installation/atom/) or VSCode [**(instructions)**](https://docs.pycom.io/pymakr/installation/vscode/)
* In the editor, open a new project in the `project` folder  
* Open `/lib/deviceId.py` and in `DEVICE_ID = "ABxy"` change the `ABxy` string to match the label on the device case
* Open `/lib/config.py` and in `LTENB_APN = "ep.inetd.gdsp"` change the string to match the correct country apn:
  * "swisscom-test.m2m.ch" for Swisscom.CH
  * "internetm2m" for Altice.PT
  * "ep.inetd.gdsp" for Vodafone.IE
* Connect to the board and upload the project
