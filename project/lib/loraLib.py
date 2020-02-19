import _thread
import gc
from network import LoRa
import socket
import binascii
import struct
import time
import ujson as json
import machine
import wifi
import config
import state
from logger import Logger

class Loralib:
    """
    __init__
        Does not receive any parameters
        return lora
        In this function LoRa is Initialize  in LORAWAN mode, the channels are prepared,
        and the node tries to join the network
    """
    def __init__(self):
        #enable logger
        self.log = Logger()
        self.lora = None
        self.s = None
        self.lora_ping = True
        try: # Initialize LoRa in LORAWAN mode.This class provides a LoRaWAN 1.0.2
            self.lora = LoRa(mode=LoRa.LORAWAN,device_class=LoRa.CLASS_C,adr=True)
        except Exception as e1:
            self.lora = None
            self.log.debugLog("initLoRa Failed")
        '''
        try:
            self.log.debugLog("LoRa init: Trying lora.nvram_restore")
            self.lora.nvram_restore()           
        except Exception as e:
            self.log.debugLog("lora.nvram_restore Failed: {}".format(e))
        '''
        if not self.lora.has_joined():                
            self.log.debugLog("LoRa init: Not joined yet.")
            try:
                                # set the  default channels to the same frequency
                self.lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
                self.lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
                self.lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)
                self.lora.add_channel(3, frequency=868300000, dr_min=0, dr_max=5)
            except Exception as e:
                self.lora = None
                self.log.debugLog("prepare_channels Failed: {}".format(e))
                #In case of failure prepare the channels again
                #self.lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
                #self.lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
                    #self.lora.add_channel(2, frequency=868300000, dr_min=0, dr_max=5)
            try:
                for c in range(4, 16):
                    self.lora.remove_channel(c)
                    # join a network using OTAA
                    self.lora.join(activation=self.lora.OTAA, auth=(self.OTAAauth()), timeout=0)           
                    self.log.debugLog("LoRa init: Joining...")
                    # wait until the module has joined the network max time 100 sec
                    i=0
                    while not self.lora.has_joined():
                        time.sleep(4)
                        i += 1
                        print("Not joined yet...",i)
                        if(i>=10):
                            time.sleep(2)
                        if(i==20):
                            raise Exception("Failed to join LoRa Network")
                    break						
            except Exception as e:
                self.lora = None
                self.log.debugLog("LoRa join Failed: {}".format(e))
        if self.lora.has_joined():           
            self.log.debugLog("LoRa init: Joined.")
            try:
                self.s = self.createSocket()
                if self.s is not None:
                    #state.CONNECTED = True
                    state.LORA_CONNECTED = True
            except Exception as e:
                self.lora = None
                self.log.debugLog("createSocket Failed: {}".format(e))

    """
    OTAAauth :
        Input parameter: (Optional) [String] DeviceId (Default = "node1")
        Returns dev_eui,app_eui,app_key necessary for OTA (over the air activation ),
        please choose your device in this function
    """
    def OTAAauth(self):
        try:
            app_eui = config.APP_EUI
            dev_eui = config.DEV_EUI
            app_key = config.APP_KEY
            return dev_eui,app_eui,app_key
        except Exception as e2:
            self.log.debugLog("Failed to create OTA authentication please check your dev_eui,app_eui and app_key")

    '''
    createSocket:
        Does not receive any parameters
        return s
        In this function a socket is Initialize
    '''
    def createSocket(self):
        try:
            s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
            # set the LoRaWAN data rate
            s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
            # make the socket blocking
            s.setblocking(False)
            time.sleep(5.0)
            self.log.debugLog("Socket created ")
            return s
        except Exception as e:
            self.log.debugLog("CreateSocket Failed ", p=False)
            return None
			
    '''
    stopSocket:
        receive the Socket
        In this function a socket is closed
    '''
    def stopSocket(self):
        self.s.close()

    '''
    loraLogic:
        loraLogic inputs: timestamp, location, batteryLevel, accelerometer
            timestamp="2019-12-05T08:32:58Z"
            location is lat, lon, alt, hdop,vdop,pdop
            location ="0.000000,0.000000,0.000000,0.000000,0.000000,0.000000"
            batteryLevel="3.311792"
            accelerometer="-0.442749,0.1876221,0.8468018"
        Where the packet is send or received
        Check if there is wifiAPs
        Send to TTN max 242 bytes
        Receive from TTN
    '''
    def loraLogic(self, timestamp='1970-01-01T00:00:00Z', lat='0', lon='0', alt='0', hdop='0', vdop='0', pdop='0', batteryLevel='0', x='0', y='0', z='0'):
        if state.LORA_CONNECTED:
            location = lat +","+ lon +","+ alt +","+ hdop +","+ vdop +","+ pdop
            accelerometer = x +","+ y +","+ z
            wifiAPs = None
            if state.WIFI_ACTIVE:   
                #check if there is wifi
                wifiAPs = wifi.wifiAPsLoRa()
            if wifiAPs is not None:
                pkt_status = bytes(wifiAPs) + "," + timestamp + "," + location + "," + batteryLevel + "," + accelerometer
            else:
                pkt_status = timestamp + "," + location + "," + batteryLevel + "," + accelerometer
            '''
            Transmit the packet
            '''
            self.s.send(pkt_status)
            self.log.debugLog('LoRa Uplink: {}'.format(pkt_status))
            time.sleep(1)
            # save lora state
            #self.lora.nvram_save()
            '''
            Check msg counter
            '''
            try:
                stats = self.lora.stats()
                self.log.debugLog("LoRa stats: {}".format(stats))
                counter = stats.tx_counter
                if (counter % 10) == 0:
                    if self.lora_ping is True:
                        self.lora_ping = False
                    else:
                        self.log.debugLog("Lora ping timeout... going to sleep.")
                        time.sleep(1)
                        machine.deepsleep(config.DEEP_SLEEP)
            except Exception as e:
                self.log.debugLog("lora.stats Failed: {}".format(e))
            '''
            Receive a packet
            '''
            rx = None
            try:
                rxb = self.s.recv(500)
                rx = rxb.decode('uft-8')
                #rx = str(rxb,'uft-8')
            except Exception as error:
                self.log.debugLog('Exception loraLib s.recv: {}'.format(error))
                rx = None
            #weird way to check if message was received (aka rx = (null))
            if '{}'.format(rx) is '(null)':
                rx = None 
            if '{}'.format(rx) is '':
                rx = None 
            if '{}'.format(rx) is 'ping':
                self.log.debugLog('LoRa ping received')
                self.lora_ping = True
                rx = None

            # return received msg
            return rx
        else:
            return None

    '''
    processRecvMsg:
        input: msg as string with json object containing the topic and payload
        processes the msg according to the topic and payload
    '''
    def processRecvMsg(self, msg):
        if msg is not None:
            self.log.debugLog('processRecvMsg: {}'.format(msg))
            try:
                json_obj_msg = json.loads(msg)
            except ValueError as valueerror:
                self.log.debugLog('Exception loraLib json valueerror: {}'.format(valueerror))
            else:
                try:
                    json_obj = json_obj_msg['configuration/energyProfile']
                except KeyError as keyerror:
                    self.log.debugLog('Exception loraLib json keyerror msg: {}'.format(keyerror))
                else:
                    try:
                        state.GNSS_ACTIVE = json_obj['gnss']['active']
                        config.GNSS_SR = json_obj['gnss']['sr']
                        state.LTENB_ACTIVE = json_obj['lteNB']['active']
                        config.LTENB_SR = json_obj['lteNB']['sr']
                        state.WIFI_ACTIVE = json_obj['wifi']['active']
                        config.WIFI_SR = json_obj['wifi']['sr']
                        state.LORA_ACTIVE = json_obj['lora']['active']
                        config.LORA_SR = json_obj['lora']['sr']
                    except KeyError as keyerror:
                        self.log.debugLog('Exception loraLib json keyerror obj: {}'.format(keyerror))
