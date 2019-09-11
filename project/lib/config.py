import deviceId
# NTP SERVER CONFIG
NTP_SERVER = "87.44.18.206" # "87.44.18.206"  TSSG Carelink NTP server # Alternative: "0.europe.pool.ntp.org"
# MQTT CONFIG
MQTT_DEVICE_ID = deviceId.DEVICE_ID
MQTT_SERVER = "87.44.18.29" # "87.44.18.29" #"mqtt.staging.carelink.tssg.org"
MQTT_USER_ID = None # Replace with mqtt username for authentication with the broker
MQTT_PWD = None # Replace with mqtt password for authentication with the broker
# MQTT Topics
MQTT_PUB_STATUS = MQTT_DEVICE_ID + "/status"
MQTT_SUB_ACTIVE = MQTT_DEVICE_ID + "/active"
MQTT_SUB_CONF_ENERGY = MQTT_DEVICE_ID + "/configuration/energyProfile"
MQTT_SUB_CONF_WIFI = MQTT_DEVICE_ID + "/configuration/wifi"
# MQTT PUB SR
MQTT_PUB_SR = 30
# WLAN CONFIG
SSID = "PwD Home Wifi SSID"
WLANPWD = "PwD Home Wifi Password"
# LTE-NB CONFIG
LTENB_APN = "ep.inetd.gdsp" # "swisscom-test.m2m.ch" for Swisscom.CH; "internetm2m" for Altice.PT; "̶v̶o̶d̶a̶f̶o̶n̶e̶_̶a̶p̶n̶" "ep.inetd.gdsp" for Vodafone.IE
# ENERGY PROFILE DEFAULT CONFIG
GNSS_SR = 10
LTENB_SR = 30
WIFI_SR = 30
