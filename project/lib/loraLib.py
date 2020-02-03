import _thread
import gc
from network import LoRa
import socket
import binascii
import struct
import time
import ujson as json
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
        try: # Initialize LoRa in LORAWAN mode.This class provides a LoRaWAN 1.0.2
            self.lora = LoRa(mode=LoRa.LORAWAN,device_class=LoRa.CLASS_C,adr=True)
            try:
                                # set the  default channels to the same frequency
                self.lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
                self.lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
                self.lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)
                self.lora.add_channel(3, frequency=868300000, dr_min=0, dr_max=5)

                for c in range(4, 16):
                    self.lora.remove_channel(c)

                    try:
                        # join a network using OTAA
                        self.lora.join(activation=self.lora.OTAA, auth=(self.OTAAauth()), timeout=0)
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

                        self.s = self.createSocket()
                        if self.s is not None:
                            #state.CONNECTED = True
                            state.LORA_CONNECTED = True
                        break
						
                    except Exception as e3:
                        self.lora = None
                        self.log.debugLog("{}".format(e3))
            except Exception as e2:
                self.lora = None
                self.log.debugLog("prepare_channels Failed")
                #In case of failure prepare the channels again
                #self.lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
                #self.lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
                #self.lora.add_channel(2, frequency=868300000, dr_min=0, dr_max=5)
        except Exception as e1:
            self.lora = None
            self.log.debugLog("initLoRa Failed")
            #In case of failure run

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
            print('Sending:', pkt_status)
            time.sleep(1)

            #pkt = b'PKT #' + bytes([i])
            #print(lora.stats())
            #(rx_timestamp=127533922, rssi=-42, snr=8.0, sfrx=3, sftx=5, tx_trials=0, tx_power=0, tx_time_on_air=241, tx_counter=14,tx_frequency=0)
            #can be used for debug

            '''
            Receive a packet
            '''
            rx = None
            try:
                rx = str(self.s.recv(256), 'uft-8')
            except OSError as scktError:
                self.log.debugLog('Exception loraLib s.recv: {}'.format(scktError))
                rx = None
            except Exception as error:
                self.log.debugLog('Exception loraLib s.recv: {}'.format(error))
                rx = None
            #weird way to check if message was received (aka rx = (null))
            if '{}'.format(rx) is '(null)':
                rx = None 
            #print(rx)
            #time.sleep(5)
            return rx
        else:
            return None

    '''
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
