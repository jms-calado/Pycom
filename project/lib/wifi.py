from network import WLAN
import binascii
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

def wifiAPsLoRa(wlan = None):
    if wlan == None:
        try:
            wlan = WLAN(mode=WLAN.STA)
        except Exception as e:            
            log.debugLog("Failed to start wifi for LoRa ")
            return None
    try:        
        ssids = wlan.scan()
    except Exception as e:
        log.debugLog("Failed to get wifiAPs for LoRa ")
        return None

    #BSSID 0
    a=ssids[0][1]
    a=binascii.hexlify(a)
    res=[]
    for i in range (12):
        if (i%2) == 0:
            aux=int(a[i:i+2], 16)
            res.append(aux)
        else:
             pass
    #RSSI0
    a=ssids[0][4]
    RSSI0 = -a
    res.append(RSSI0)
    #BSSID 1
    a=ssids[1][1]
    a=binascii.hexlify(a)
    for i in range (12):
        if (i%2) == 0:
            aux=int(a[i:i+2], 16)
            res.append(aux)
        else:
             pass
    BSSID1=int(a, 16)
    #RSSI 1
    a=ssids[1][4]
    RSSI1 = -a
    res.append(RSSI1)
    #BSSID 2
    a=ssids[2][1]
    a=binascii.hexlify(a)
    for i in range (12):
        if (i%2) == 0:
            aux=int(a[i:i+2], 16)
            res.append(aux)
        else:
             pass		 
    BSSID2=int(a, 16)
    #RSSI 2
    a=ssids[2][4]
    RSSI2 = -a
    res.append(RSSI2)
    '''
    if not state.WIFI_ACTIVE:
        disconnectWifi(wlan)
    '''
    disconnectWifi(wlan) #remove if using Wifi for comms
    return res

'''
Example out : ""wifiAPs":{"mac_1":"04:92:26:66:be:88","rssi_1":-67,"mac_2":"06:92:26:76:be:88","rssi_2":-67,"mac_3":"00:06:91:fa:5f:d0","rssi_3":-76}"
Used to mount status message when LoRa is not in used
'''
def wifiAPs(wlan = None):
    if wlan == None:
        try:
            wlan = WLAN(mode=WLAN.STA)
        except Exception as e:            
            log.debugLog("Failed to start wifi for LoRa ")
            return None
    try:
        ssids = wlan.scan()
    except Exception as e:
        log.debugLog("Failed to get wifiAPs ")
        return None
    #BSSID 1
    a=ssids[0][1]
    a=binascii.hexlify(a)
    res="\"wifiAPs\":{\"mac_1\":\""
    for i in range (12):
        if(i==10):
            aux=str(a[i:i+2],16)
            res+=aux+"\""+","
        else:
            if (i%2) == 0:
                aux=str(a[i:i+2],16)
                res+=aux+":"
            else:
                pass
    #RSSI 1
    a=ssids[0][4]
    RSSI1 =str(a)
    res+="\"rssi_1\":"+RSSI1+",\"mac_2\":\""
    #BSSID 2
    a=ssids[1][1]
    a=binascii.hexlify(a)
    for i in range (12):
        if(i==10):
            aux=str(a[i:i+2],16)
            res+=aux+"\""+","
        else:
            if (i%2) == 0:
                aux=str(a[i:i+2],16)
                res+=aux+":"
            else:
                pass
    #RSSI 2
    a=ssids[1][4]
    RSSI2 =str(a)
    res+="\"rssi_2\":"+RSSI2+",\"mac_3\":\""
    #BSSID 3
    a=ssids[2][1]
    a=binascii.hexlify(a)
    for i in range (12):
        if(i==10):
            aux=str(a[i:i+2],16)
            res+=aux+"\""+","
        else:
            if (i%2) == 0:
                aux=str(a[i:i+2],16)
                res+=aux+":"
            else:
                pass
    #RSSI 3
    a=ssids[2][4]
    RSSI3 =str(a)
    res+="\"rssi_3\":"+RSSI3+"}"
    '''
    if not state.WIFI_ACTIVE:
        disconnectWifi(wlan)
    '''
    disconnectWifi(wlan) #remove if using Wifi for comms
    return res