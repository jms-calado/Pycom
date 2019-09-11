from network import WLAN
import machine
import time
import config
import state
from logger import Logger

#enable logger
log = Logger()

# Connect to WLAN
def connectWifi():
    wlan = WLAN(mode=WLAN.STA)
    ssids = wlan.scan()
    for ssid in ssids:
        print(ssid.ssid)
        if ssid.ssid == config.SSID:
            log.debugLog('WLAN: Network found!')
            wlan.connect(ssid.ssid, auth=(ssid.sec, config.WLANPWD), timeout=5000)
            while not wlan.isconnected():
                machine.idle() # save power while waiting
            state.CONNECTED = True
            log.debugLog('WLAN: Connection succeeded!')
            #break
            return wlan
        else:
            log.debugLog('WLAN: Network not found!')

def disconnectWifi(wlan):
    if wlan.isconnected():
        state.CONNECTED = False
        wlan.disconnect()
    wlan.deinit()
