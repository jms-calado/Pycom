import binascii

#DeviceId
DEVICE_ID = "DEVICE_ID"

MQTT_USER_ID = "MQTT_USER_ID"
MQTT_PWD = "MQTT_PWD"

SSID = "WLAN SSID"
WLANPWD = "WLAN PWD"

LTENB_APN = "ep.inetd.gdsp" #"swisscom-test.m2m.ch" for Swisscom CH; "internetm2m" for Altice PT; "̶v̶o̶d̶a̶f̶o̶n̶e̶_̶a̶p̶n̶" "ep.inetd.gdsp" for Vodafone IE

# create an OTA authentication params.  these settings can be found from TTN
APP_EUI = binascii.unhexlify('APP_EUI')
DEV_EUI = binascii.unhexlify('DEV_EUI')
APP_KEY = binascii.unhexlify('APP_KEY')