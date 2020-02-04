import _thread
import time
import utime
import gc
import os
import pycom
import ujson as json
from machine import Timer
from umqttrobust import MQTTClient
from logger import Logger
import config
import state
import wifi


class MQTTLogic:

    # enable GC
    gc.enable()

    def __init__(self, client = None):
        self.client = client
        #self.log = log
        #enable logger
        self.log = Logger()

    #mqtt sub callback
    def sub_cb(self, topic, msg):
        #print("topic: " + str(topic))
        #print("msg: " + str(msg))
        self.log.debugLog('Sub Topic: {} ||| Msg: {}'.format(topic.decode(), msg.decode()))
        if topic == config.MQTT_SUB_ACTIVE.encode():
            if msg == b'true':
                state.OP_MODE = True
                pycom.nvs_set('active', 1)
                self.stopMQTT()
            elif msg == b'false':
                state.OP_MODE = False
                pycom.nvs_set('active', 0)
                pycom.nvs_set('bootNum', 0)
        elif topic == config.MQTT_SUB_CONF_ENERGY.encode():
            try:
                json_obj = json.loads(msg.decode())
            except ValueError as valueerror:
                self.log.debugLog('Exception MQTT json valueerror: {}'.format(valueerror))
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
                self.log.debugLog('Exception MQTT json keyerror: {}'.format(keyerror))
        elif topic == config.MQTT_SUB_CONF_WIFI.encode():
            try:
                json_obj = json.loads(msg.decode())
            except ValueError as valueerror:
                self.log.debugLog('Exception MQTT json valueerror: {}'.format(valueerror))
            try:
                config.SSID = json_obj['ssid']
                config.WLANPWD = json_obj['wlanpw']
            except KeyError as keyerror:
                self.log.debugLog('Exception MQTT json keyerror: {}'.format(keyerror))

    # MQTT connect
    def startMQTT(self):
        self.log.debugLog('start mqtt')
        if state.CONNECTED:
            try:
                self.client = MQTTClient(client_id=config.MQTT_DEVICE_ID, server=config.MQTT_SERVER, user=config.MQTT_USER_ID, password=config.MQTT_PWD, port=1883, keepalive=600)
                self.client.set_callback(self.sub_cb)
                #ed_id = config.MQTT_DEVICE_ID
                #lw_msg = '{"status":"Unexpected disconnection:' + ed_id + '"}'
                #lw_msg = '{"status":"123456789012345proto1"}'
                lw_msg = '"LW: Unexpected disconnect"'
                self.client.set_last_will(topic=config.MQTT_PUB_STATUS, msg=lw_msg, retain=False, qos=1)
                #if self.client.connect(clean_session=False):
                #    raise Exception('MQTT connect: a session already exists')
                conn_result = self.client.connect(clean_session=False)
                self.log.debugLog('conn_result: {}'.format(conn_result))
            except OSError as oserror:
                try:
                    if oserror.errno == errno.EHOSTUNREACH:
                        # MQTT Connect Failed because Host is unreachable.
                        self.log.debugLog('Exception MQTT Connect EHOSTUNREACH: {}'.format(oserror))
                        state.MQTT_ACTIVE = False
                        return state.MQTT_ACTIVE
                    else:
                        self.log.debugLog('Exception MQTT Connect OSError: {}'.format(oserror))
                        state.MQTT_ACTIVE = False
                        return state.MQTT_ACTIVE
                except AttributeError as atterr:
                    self.log.debugLog('Exception MQTT Connect AttributeError: {}'.format(atterr))
                    state.MQTT_ACTIVE = False
                    return state.MQTT_ACTIVE
            except Exception as mqttconnecterror:
                self.log.debugLog('Exception MQTT Connect: {}'.format(mqttconnecterror))
                #self.log.debugLog(mqttconnecterror)
                state.MQTT_ACTIVE = False
                return state.MQTT_ACTIVE
            self.log.debugLog('MQTT: connected')
            try:
                self.client.subscribe(topic=config.MQTT_SUB_ACTIVE, qos=1)
                time.sleep(1)
            except Exception as mqttpubsuberror:
                self.log.debugLog('Exception MQTT_SUB_ACTIVE: {}'.format(mqttpubsuberror))
                state.MQTT_ACTIVE = False
                return state.MQTT_ACTIVE
            try:
                self.client.subscribe(topic=config.MQTT_SUB_CONF_ENERGY, qos=1)
                time.sleep(1)
            except Exception as mqttpubsuberror:
                self.log.debugLog('Exception MQTT_SUB_CONF_ENERGY: {}'.format(mqttpubsuberror))
                state.MQTT_ACTIVE = False
                return state.MQTT_ACTIVE
            try:
                self.client.subscribe(topic=config.MQTT_SUB_CONF_WIFI, qos=1)
                time.sleep(1)
            except Exception as mqttpubsuberror:
                self.log.debugLog('Exception MQTT_SUB_CONF_WIFI: {}'.format(mqttpubsuberror))
                state.MQTT_ACTIVE = False
                return state.MQTT_ACTIVE
            self.log.debugLog('MQTT: subbed')
            '''
            try:
                registered = pycom.nvs_get('registered')
            except Exception as nvserror:
                registered = None
            self.log.debugLog('MQTT registered: {}'.format(registered))
            if registered == None:
                msg_reg = '{"deviceId":"' + config.MQTT_DEVICE_ID + '","component":["lteNB","lora","wifi","bluetooth","accelerometer","gnss"],"batteryCapacity":800}'
                self.client.publish(topic=config.MQTT_PUB_REG, msg=msg_reg, retain=False, qos=1)
                pycom.nvs_set('registered', 1)
            '''
            if not state.OP_MODE:
                try:
                    # start thread
                    self.runThread = True
                    self.mqttLogic_thread = _thread.start_new_thread(self.mqtt_thread,())
                except Exception as mqttstartthread:
                    self.log.debugLog('Exception MQTT start thread: {}'.format(mqttstartthread))
                    state.MQTT_ACTIVE = False
                    return state.MQTT_ACTIVE

            state.MQTT_ACTIVE = True
            return state.MQTT_ACTIVE

    def mqtt_thread(self):
        self.thread_active = True
        print('Running mqtt_thread id: {}'.format(_thread.get_ident()))
        while self.runThread:
            gc.collect()
            self.client.check_msg() #check SUBed messages
            if not self.runThread:
                self.log.debugLog("Breaking thread loop")
                break
            time.sleep(config.MQTT_PUB_SR)
        try:
            self.log.debugLog("Try to exit MQTT thread")
            self.thread_active = False
            _thread.exit()
        except SystemExit as sysexiterror:
            self.log.debugLog('System Exit: {}'.format(sysexiterror))
            self.log.debugLog('Exited mqtt_thread id: {}'.format(_thread.get_ident()))
        time.sleep(1)
        '''
        if not self.thread_active:
            if state.MQTT_ACTIVE:
                self.client.disconnect()
                self.log.debugLog("Try to disconnect MQTT client")
        '''

    def stopMQTT(self):
        self.runThread = False
        time.sleep(5)
        #if state.MQTT_ACTIVE:
        #    self.client.disconnect()
        self.log.debugLog('end mqtt')

    def pubMQTT(self, topic, msg, retain, qos):
        #self.log.debugLog('pubMQTT check_msg')
        self.client.check_msg() #check SUBed messages
        if state.MQTT_ACTIVE:
            try:
                self.client.publish(topic, msg, retain, qos)
                self.log.debugLog('Pub Topic: {} // Msg: {} // Retain: {} // QoS: {}'.format(topic, msg, retain, qos))
            except Exception as e:
                self.log.debugLog(e)

    def pingMQTT(self):
        if state.MQTT_ACTIVE:
            try:
                self.client.ping()
            except Exception as e:
                self.log.debugLog(e)
            try:
                res = self.client.wait_msg()
                if(res == b"PINGRESP") :
                    self.log.debugLog('Ping Successful')
                else:
                    self.log.debugLog('Ping response: {}'.format(res))
            except Exception as e:
                self.log.debugLog(e)

    def pubStatus(self, timestamp='1970-01-01T00:00:00Z', lat='0', lon='0', alt='0', hdop='0', vdop='0', pdop='0', batteryLevel='0', x='0', y='0', z='0'):
        try:
            statusMsg = '{"timestamp":"' + timestamp + '","location":{"lat":' + lat + ',"lon":' + lon + ',"alt":' + alt + ',"hdop":' + hdop + ',"vdop":' + vdop + ',"pdop":' + pdop + '},"batteryLevel":' + batteryLevel + ',"sensor":{"accelerometer":{"x":' + x + ',"y":' + y + ',"z":' + z + '}}}'
            #statusMsg = '{"timestamp":"{}","location":{"lat":{},"lon":{},"alt":{},"hdop":{},"vdop":{},"pdop":{}},"batteryLevel":{}}'.format(timestamp, lat, lon, alt, hdop, vdop, pdop, batteryLevel)
            if state.WIFI_ACTIVE:
                wifiAPs = None
                #check if there is wifi
                wifiAPs = wifi.wifiAPs()
                if wifiAPs is not None:
                    statusAPs = '{"timestamp":"' + timestamp + '","location":{"lat":' + lat + ',"lon":' + lon + ',"alt":' + alt + ',"hdop":' + hdop + ',"vdop":' + vdop + ',"pdop":' + pdop + '},"batteryLevel":' + batteryLevel + ',"sensor":{"accelerometer":{"x":' + x + ',"y":' + y + ',"z":' + z + '}},' + wifiAPs + '}'
                    self.pubMQTT(topic=config.MQTT_PUB_STATUS_WIFIAPS, msg=statusAPs, retain=False, qos=0)
                else:
                    self.pubMQTT(topic=config.MQTT_PUB_STATUS, msg=statusMsg, retain=False, qos=0)
            else:
                self.pubMQTT(topic=config.MQTT_PUB_STATUS, msg=statusMsg, retain=False, qos=0)
        except Exception as e:
            self.log.debugLog('Status PUB Exception: {}'.format(e))
