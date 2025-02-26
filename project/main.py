# Device Libs
import time
import utime
import usocket
import gc
import os
import pycom
import machine
from machine import RTC, SD, Timer
from network import LTE
# Custom Libs:
from pytrack import Pytrack
from L76micropyGPS import L76micropyGPS
from micropyGPS import MicropyGPS
from MQTTLogic import MQTTLogic
from logger import Logger
from loraLib import Loralib
import config
import state
import nb
import wifi

print('### main.py ###')

# enable logger
log = Logger()

# enable GC
gc.enable()

log.debugLog("Free Mem: {}".format(gc.mem_free()))

pycom.heartbeat(False)
pycom.rgbled(0xffff00) # yellow led

# Set DNS
#usocket.dnsserver(0,'8.8.8.8')
#usocket.dnsserver(1,'4.4.4.4')

# Set OP_MODE
try:
    active = pycom.nvs_get('active')
except Exception as nvserror:
    active = None
    log.debugLog('MQTT activated nvserror: {}'.format(nvserror))
if active is not None:
    if active == 1:
        state.OP_MODE = True
        log.debugLog('MQTT activated: True')

# LTE
if state.LTENB_ACTIVE:
    lte = nb.startLTE()
'''
# WiFi
if state.WIFI_ACTIVE:
    wlan = wifi.connectWifi()
'''
loralib = None
'''
# LoRa
if state.LORA_ACTIVE:
    loralib = Loralib()
    
    if loralib.lora is not None:
        loralib.loraLogic("2019-12-12T08:32:58Z","1.000000,0.000000,0.000000,0.000000,0.000000,0.000000","3.311792","0.442749,0.1876221,0.8468018")
    else:
        #handle lora=None failure
        pass
'''
# Set RTC
rtc = RTC()

# If not connected, disable LTE and sleep for 2 hours
if not state.CONNECTED:
    # If not LoRa is not used
    if not state.LORA_ACTIVE:
        try:
            lte
        except NameError:
            #pass
            machine.reset()
        else:
            nb.endLTE(lte)
        time.sleep(1)
        machine.deepsleep(config.DEEP_SLEEP)
    # If LoRa is used and OP_MODE == True (MQTT Active)
    elif state.OP_MODE:
        nb.endLTE(lte)
        loralib = Loralib()        
        if loralib.lora is not None and state.LORA_CONNECTED:
            state.CONNECTED = True
        else:
            time.sleep(1)
            machine.deepsleep(config.DEEP_SLEEP)
    else:
        time.sleep(1)
        machine.deepsleep(config.DEEP_SLEEP)

# If connected, set: RTC; MQTT connection; GNSS. Start Normal Op Mode
if state.CONNECTED:
    mqttLogic = None
    # If not LoRa is not used
    if not state.LORA_CONNECTED:
        # RTC
        pycom.rgbled(0xff) # dark blue led
        #log.debugLog("Initial RTC: {}".format("set" if rtc.synced() else "unset"))
        if not rtc.synced():
            import rtcLib
            rtc = rtcLib.getRTC(rtc)
            log.debugLog("RTC: {}".format(rtc.now() if rtc.synced() else "unset"))

        # MQTT connect
        pycom.rgbled(0xff00) # green led
        mqttLogic = MQTTLogic()
        activewait = False
        for counter in range(3): # repeat startMQTT at most 3 times
            mqttactive = mqttLogic.startMQTT()
            if mqttactive:
                break
            else:
                time.sleep(30)
        if not state.OP_MODE:
            activewait = True
            log.debugLog("Awaiting Activation")
        while not state.OP_MODE:
            time.sleep(30)
        if state.OP_MODE and activewait:
            log.debugLog("Activated. Stoping mqtt thread.")
            mqttLogic.stopMQTT()
            time.sleep(1)
        log.debugLog("Resuming Normal Operation Mode")

        log.debugLog("Free Mem: {}".format(gc.mem_free()))

    pycom.rgbled(0x00ffff) # light blue led

    if state.GNSS_ACTIVE: # and state.OP_MODE:
        # Start a microGPS object
        my_gps = MicropyGPS(location_formatting='dd')
        # Start the L76micropyGPS object
        l76gps = L76micropyGPS(my_gps)
        # Start the GPS thread
        #gpsThread = l76gps.startGPSThread()
        log.debugLog('Aquiring GPS signal')
        # Start the Pub thread
        l76gps.startPubThread(mqttLogic, loralib)
        pycom.rgbled(0x000000) # off led
        pycom.heartbeat(True)
    '''
    # start a timer
    chrono = Timer.Chrono()
    chrono.start()
    elapsed = chrono.read()
    print('Elapsed: {}'.format(elapsed))
    '''
    # STATE MACHINE LOOP:
    last_state_gnss = state.GNSS_ACTIVE
    last_state_ltenb = state.LTENB_ACTIVE
    last_state_lora = state.LORA_ACTIVE
    last_state_wifi = state.WIFI_ACTIVE
    last_state_mqtt = state.MQTT_ACTIVE
    last_config_gnss_sr = config.GNSS_SR
    while(state.OP_MODE):
        if last_state_gnss is not state.GNSS_ACTIVE:
            log.debugLog('last_state_gnss: {} is not state.GNSS_ACTIVE: {}'.format(last_state_gnss, state.GNSS_ACTIVE))
            if state.GNSS_ACTIVE:
                # Start the GPS thread
                #gpsThread = l76gps.startGPSThread()
                log.debugLog('Aquiring GPS signal')
                # Start the Pub thread
                l76gps.startPubThread(mqttLogic, loralib)
            else:
                l76gps.stopPubThread()
                time.sleep(1)
                #l76gps.stopGPSThread()
                #time.sleep(1)
        if last_state_ltenb is not state.LTENB_ACTIVE:
            log.debugLog('last_state_ltenb: {} is not state.LTENB_ACTIVE: {}'.format(last_state_ltenb, state.LTENB_ACTIVE))
            if state.LTENB_ACTIVE:
                lte = nb.startLTE()
            else:
                nb.endLTE(lte)
        '''
        if last_state_wifi is not state.WIFI_ACTIVE:
            log.debugLog('last_state_wifi: {} is not state.WIFI_ACTIVE: {}'.format(last_state_wifi, state.WIFI_ACTIVE))
            if state.WIFI_ACTIVE:
                wlan = wifi.connectWifi()
            else:
                wifi.disconnectWifi(wlan)
        if last_config_gnss_sr is not config.GNSS_SR:
            log.debugLog('last_config_gnss_sr: {} is not config.GNSS_SR: {}'.format(last_config_gnss_sr, config.GNSS_SR))
            pass #TO-DO: define function to change GNSS sample rate
        '''
        if state.LTENB_ACTIVE:
            if config.MQTT_PUB_SR is not config.LTENB_SR:
                log.debugLog('config.MQTT_PUB_SR: {} is not config.LTENB_SR: {}'.format(config.MQTT_PUB_SR, config.LTENB_SR))
                config.MQTT_PUB_SR = config.LTENB_SR
        elif state.LORA_ACTIVE:
            if config.MQTT_PUB_SR is not config.LORA_SR:
                log.debugLog('config.MQTT_PUB_SR: {} is not config.LORA_SR: {}'.format(config.MQTT_PUB_SR, config.LORA_SR))
                config.MQTT_PUB_SR = config.LORA_SR
        '''
        if state.WIFI_ACTIVE:
            if config.MQTT_PUB_SR is not config.WIFI_SR:
                log.debugLog('config.MQTT_PUB_SR: {} is not config.WIFI_SR: {}'.format(config.MQTT_PUB_SR, config.WIFI_SR))
                config.MQTT_PUB_SR = config.WIFI_SR
        '''
        time.sleep(40)

    pycom.rgbled(0x7f0000) # red led

    # EXIT running connections and threads
    try:
        l76gps
    except NameError:
        pass
    else:
        l76gps.stopPubThread()
        time.sleep(1)
        l76gps.stopGPSThread()
        time.sleep(1)
    mqttLogic.stopMQTT()
    time.sleep(1)
    try:
        lte
    except NameError:
        pass
    else:
        nb.endLTE(lte)
    time.sleep(1)
    try:
        wlan
    except NameError:
        pass
    else:
        wifi.disconnectWifi(wlan)
    state.CONNECTED = False

log.debugLog('End RUN // {}'.format(rtc.now()))

machine.main('boot.py')
