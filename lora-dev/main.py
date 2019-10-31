""" OTAA Node example compatible with the LoPy Nano Gateway """
from network import LoRa
from network import WLAN
import socket
import binascii
import struct
import time
from CayenneLPP import CayenneLPP
from logger import Logger

#enable logger
log = Logger()


"""
OTAAauth :
Does not receive any parameters
return dev_eui,app_eui,app_key necessary for OTA (over the air activation ),
please choose your device in this function

"""

def OTAAauth():
    try:
        # create an OTA authentication params
        dev_eui = binascii.unhexlify('00 C2 38 37 41 99 33 62'.replace(' ',''))
        dev_addr = binascii.unhexlify('26 01 27 83'.replace(' ',''))

        ##please uncoment for use other node instead of node1
        ############################## CP ########################################
        #CP2
        #dev_eui = binascii.unhexlify('00 73 4E 8C 4D 5A B8 ED'.replace(' ',''))
        #CP8
        #dev_eui = binascii.unhexlify('00 64 94 3D 21 96 52 A7'.replace(' ',''))
        #CP10
        #dev_eui = binascii.unhexlify('00 9F AA 7F 08 69 88 BE'.replace(' ',''))
        #CP18
        #dev_eui = binascii.unhexlify('00 20 06 75 8D 92 0D 67'.replace(' ',''))
        #CP20
        #dev_eui = binascii.unhexlify('00 AC 4B 89 18 D8 94 4F'.replace(' ',''))
        ######################### Proto
        #Proto1
        #dev_eui = binascii.unhexlify('00 C0 8B D8 8B DC A0 38'.replace(' ',''))
        #Proto2
        #dev_eui = binascii.unhexlify('00 C2 7A 69 07 75 30 0E'.replace(' ',''))



        #node2
        #dev_eui = binascii.unhexlify('00 C2 38 37 41 99 33 02'.replace(' ',''))
        #node3
        #dev_eui = binascii.unhexlify('00 C2 38 37 41 99 33 03'.replace(' ',''))
        #node4
        #dev_eui = binascii.unhexlify('00 C2 38 37 41 99 33 04'.replace(' ',''))
        #node5
        #dev_eui = binascii.unhexlify('00 C2 38 37 41 99 33 05'.replace(' ',''))



        app_eui = binascii.unhexlify('70 B3 D5 7E D0 01 FB EE'.replace(' ','')) # these settings can be found from TTN

        app_key = binascii.unhexlify('56 95 CC 30 E5 1D 9B A3 A0 77 75 70 F4 86 5E 87'.replace(' ','')) # these settings can be found from TTN

        #####################################################  CP   ###############################################################################
        #CP2
        #app_key = binascii.unhexlify('53 4A 8D BB 7D 7A 0D 0D BD 8A 93 3D 55 C1 EF 87'.replace(' ','')) # these settings can be found from TTN
        #CP8
        #app_key = binascii.unhexlify('F4 3D C8 63 A3 21 A7 AC 93 E3 AA 3B 92 B5 0E BA'.replace(' ','')) # these settings can be found from TTN
        #CP10
        #app_key = binascii.unhexlify('15 A5 90 2E DE 90 9B 9E 99 37 1A 1C 3B 6A 18 1F'.replace(' ','')) # these settings can be found from TTN
        #CP18
        #app_key = binascii.unhexlify('8A B8 50 BD 57 CB 2E 12 D4 03 6D E4 EE 60 39 41'.replace(' ','')) # these settings can be found from TTN
        #CP20
        #app_key = binascii.unhexlify('82 A1 53 0E E8 8F 23 A1 BA 4D 9B 4E D5 1B A8 A8'.replace(' ','')) # these settings can be found from TTN
        ################################################## Proto ##################################################################################
        #Proto1
        #app_key = binascii.unhexlify('08 82 E0 66 75 03 DB C1 29 13 85 05 4B 18 69 1A'.replace(' ','')) # these settings can be found from TTN
        #Proto2
        #app_key = binascii.unhexlify('EF C1 3F 48 6A 87 0E 71 1A 43 4D 8D DE 4D 12 A8'.replace(' ','')) # these settings can be found from TTN
        ################################################ node ###################################################################################
        #node2
        #app_key = binascii.unhexlify('70 75 EE 60 D1 0B DD 3D 9D 5C 02 D2 19 DC 60 33'.replace(' ','')) # these settings can be found from TTN
        #node3
        #app_key = binascii.unhexlify('5C AE EE CA 9C 5F F1 50 EF DD 9A CC F5 B8 CC 4D'.replace(' ','')) # these settings can be found from TTN
        #node4
        #app_key = binascii.unhexlify('40 D5 9E 9B AF 45 CB 03 E7 5F 24 9A 21 39 3B 9C'.replace(' ','')) # these settings can be found from TTN
        #node5
        #app_key = binascii.unhexlify('3A 38 89 42 6F DC 54 FE DF 34 11 56 96 B2 D5 70'.replace(' ','')) # these settings can be found from TTN

        return dev_eui,app_eui,app_key;
    except Exception as e2:
        print("Failed to create OTA authentication please check your dev_eui,app_eui and app_key")
        log.debugLog("OTAA Failed ", p=False)




"""
initLoRa:
Does not receive any parameters
return lora
In this function LoRa is Initialize LoRa in LORAWAN mode, the channels are prepared,
and the node tries to join the network

"""


def InitLoRa():
    try: # Initialize LoRa in LORAWAN mode.
        lora = LoRa(mode=LoRa.LORAWAN,device_class=LoRa.CLASS_C)
        try:
            #instead of prepare_channels just put
            #
            # set the 3 default channels to the same frequency (must be before sending the OTAA join request)
            #lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
            #lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
            #lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)
            # is 3x faster

            '''
            def prepare_channels(lora, channel, data_rate):
                EU868_FREQUENCIES = [
                    { "chan": 1, "fq": "868100000" },
                    { "chan": 2, "fq": "868100000" },
                    { "chan": 3, "fq": "868100000" },
                    { "chan": 4, "fq": "868500000" },
                    { "chan": 5, "fq": "867300000" },
                    { "chan": 6, "fq": "867500000" },
                    { "chan": 7, "fq": "867700000" },
                    { "chan": 8, "fq": "867900000" },
                ]
                if not channel in range(0, 9):
                    raise RuntimeError("channels should be in 0-8 for EU868")

                if channel == 0:
                    import  uos
                    channel = (struct.unpack('B',uos.urandom(1))[0] % 7) + 1

                upstream = (item for item in EU868_FREQUENCIES if item["chan"] == channel).__next__()
                return lora
            '''

                # set the 3 default channels to the same frequency
            lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
            lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
            lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)

            for i in range(3, 16):
                lora.remove_channel(i)

                try:
                    # join a network using OTAA
                    lora.join(activation=LoRa.OTAA, auth=(OTAAauth()), timeout=0)
                    # wait until the module has joined the network
                    i=0
                    while not lora.has_joined():
                        time.sleep(3)
                        i += 1
                        print("Not joined yet...",i)
                        if(i==20):
                            break;
                    return lora
                except Exception as e3:
                    print("Failed to join LoRa network ")
                    log.debugLog("join LoRa network Failed", p=False)



        except Exception as e2:
             print("Failed to prepare channels")
             log.debugLog("prepare_channels Failed ", p=False)


    except Exception as e1:
        print("Failed to Initialize LoRa")
        log.debugLog("initLoRa Failed ", p=False)

'''
CreateSocket:
Does not receive any parameters
return s
In this function a socket is Initialize
'''

def CreateSocket():
    try:
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

        # set the LoRaWAN data rate
        s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

        # make the socket blocking
        s.setblocking(False)

        time.sleep(5.0)
        return s
    except Exception as e:
        print("Failed to CreateSocket")
        log.debugLog("CreateSocket Failed ", p=False)


'''
ScanAndSort:
Does not receive any parameters
return res a list of decimal numbers
In this function we do initialize wifi in station mode, then we do a wifi scnan
the result is list of all access points in our range, by selecting the first 3
we select the ones we the best RSSI (received signal strength indication)
For the wifi API we need to send the BSSID and RSSI, for the TTN we need to send
this numbers in decimal

'''
def ScanAndSort():
    wlan = WLAN(mode=WLAN.STA)
    ssids = wlan.scan()
    ssids =ssids[0:3]
    #print(ssids)

    #BSSID 0
    #print(ssids[0][1])
    a=ssids[0][1]
    a=binascii.hexlify(a)
    #print(a)
    res=[]
    for i in range (12):
        if (i%2) == 0:
            aux=int(a[i:i+2], 16)
            res.append(aux)
        else:
             pass


    #print(BSSID0)
    #RSSI0
    #print(ssids[0][4])
    a=ssids[0][4]
    RSSI0 = -a
    res.append(RSSI0)
    #print(RSSI0)

    #BSSID 1
    #print(ssids[1][1])
    a=ssids[1][1]
    a=binascii.hexlify(a)
    #print(a)

    for i in range (12):
        if (i%2) == 0:
            aux=int(a[i:i+2], 16)
            res.append(aux)
        else:
             pass
    BSSID1=int(a, 16)
    #print(BSSID1)

    #RSSI 1
    #print(ssids[1][4])
    a=ssids[1][4]
    RSSI1 = -a
    #print(RSSI1)
    res.append(RSSI1)

    #BSSID 2
    #print(ssids[2][1])
    a=ssids[2][1]
    a=binascii.hexlify(a)
    #print(a)
    for i in range (12):
        if (i%2) == 0:
            aux=int(a[i:i+2], 16)
            res.append(aux)
        else:
             pass

    BSSID2=int(a, 16)

    #print(BSSID2)

    #RSSI 2
    #print(ssids[2][4])
    a=ssids[2][4]
    RSSI2 = -a
    res.append(RSSI2)
    #print(RSSI2)
    #print(res)


    return res


lora=InitLoRa();
s=CreateSocket();

'''
Main:
where the packet is send or received

'''
while 1:
    '''
    Transmit a packet

    '''
    #pkt = b'PKT #' + bytes([i])
    #can be used for debug

    pkt = b'{"timestamp":"YYYY-MM-DDThh:mm:ssZ","location":{"lat":0,"lon":0,"alt":0,"hdop":0,"vdop":0,"pdop":0},"batteryLevel":3,"accompanied":1}'


    print('Sending:', pkt)
    s.send(pkt)

    time.sleep(5)




    #wifi pkt
    #s.send(bytes(scanandsort()))



    #print(lora.stats())
    #(rx_timestamp=127533922, rssi=-42, snr=8.0, sfrx=3, sftx=5, tx_trials=0, tx_power=0, tx_time_on_air=241, tx_counter=14,tx_frequency=0)

    #cayenne = CayenneLPP()
    #cayenne.add_presence(10,0)
    #cayenne.add_gps(10,1.07,104,1)
    #s.send(cayenne.get_buffer())
    #lpp = CayenneLPP()                     # create a buffer of 51 bytes to store the payload

    #lpp.reset()                           # clear the buffer
    #lpp.addTemperature(1, 22.5);           # on channel 1, add temperature, value 22.5°C
    #lpp.addBarometricPressure(2, 1073.21); # channel 2, pressure
    #lpp.addGPS(10, 52.37365, 4.88650, 2)    # channel 3, coordinates

    #ttn.sendBytes(lpp.getBuffer(), lpp.getSize())

    '''
    Receive a packet

    '''

    rx = s.recv(256)
    if rx:
        print(rx)
    time.sleep(5)
