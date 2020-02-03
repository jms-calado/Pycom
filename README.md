# Pycom

## Deployment Instructions

* Install Pycom's [**pymakr**](https://docs.pycom.io/gettingstarted/installation/pymakr/) plugin on Atom [**(instructions)**](https://docs.pycom.io/pymakr/installation/atom/) or VSCode [**(instructions)**](https://docs.pycom.io/pymakr/installation/vscode/)
* In the editor, open a new project in the `/project` folder  
* Open `/lib/keys.py` and in `DEVICE_ID = "ABxy"` change the `ABxy` string to match the label on the device case
* Open `/lib/keys.py` and in `LTENB_APN = "ep.inetd.gdsp"` change the string to match the correct country apn:
  * "swisscom-test.m2m.ch" for Swisscom.CH
  * "internetm2m" for Altice.PT
  * "ep.inetd.gdsp" for Vodafone.IE
* Open `/lib/keys.py` and change the following keys to match the LoRa authorized keys:
  * `APP_EUI = binascii.unhexlify('APP_EUI')`
  * `DEV_EUI = binascii.unhexlify('DEV_EUI')`
  * `APP_KEY = binascii.unhexlify('APP_KEY')`
* Connect to the board and upload the project
