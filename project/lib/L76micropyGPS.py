import _thread
import gc
import binascii
import time
import config
import state
from machine import RTC, WDT
from MQTTLogic import MQTTLogic
from logger import Logger

# http://www.gpsinformation.org/dale/nmea.htm#GGA
# https://forum.pycom.io/topic/1626/pytrack-gps-api/12
class L76micropyGPS:

    GPS_I2CADDR = const(0x10)

    # enable GC
    #gc.enable()

    def __init__(self, my_gps, pytrack=None, sda='P22', scl='P21'):
        if pytrack is not None:
            self.i2c = pytrack.i2c
        else:
            from machine import I2C
            self.i2c = I2C(0, mode=I2C.MASTER, pins=(sda, scl))

        self.my_gps = my_gps

        #enable logger
        self.log = Logger()

        # config GPS hints
        # https://forum.pycom.io/topic/2449/changing-the-gps-frequency-and-configuring-which-nmea-sentences-the-gps-posts/7
        # Stop logging to local flash of GPS
        #self.stoplog = "$PMTK185,1*23\r\n"
        #self.i2c.writeto(GPS_I2CADDR, self.stoplog)
        self.i2c.writeto(GPS_I2CADDR, "$PMTK185,1*23\r\n")
        self.i2c.writeto(GPS_I2CADDR, bytes([0]))
        # Use GPS, GLONASS, GALILEO and GALILEO Full satellites
        #self.searchmode = "$PMTK353,1,1,1,1,0*2B\r\n"
        #self.i2c.writeto(GPS_I2CADDR, self.searchmode)
        self.i2c.writeto(GPS_I2CADDR, "$PMTK353,1,1,1,1,0*2B\r\n")
        self.i2c.writeto(GPS_I2CADDR, bytes([0]))
        # Increase output rate to 5Hz (default is 1Hz; min. is 0.1Hz)
        # (when using GPS+GLONASS+GALILEO+GALILEOfull or any combination of the previous, max. freq. is 5Hz)
        # (when using only one mode, max. freq. is 10Hz)
        self.s01 = "$PMTK220,200*2C\r\n" #5Hz=0.1sec
        self.s05 = "$PMTK220,500*2B\r\n" #2Hz=0.5sec
        self.s1 = "$PMTK220,1000*1F\r\n" #1Hz=1sec
        self.s2 = "$PMTK220,2000*1C\r\n" #0.5Hz=2sec
        self.s5 = "$PMTK220,5000*1B\r\n" #0.2Hz=5sec
        self.s10 = "$PMTK220,10000*2F\r\n" #0.1Hz=10sec
        self.i2c.writeto(GPS_I2CADDR, self.s10)
        self.i2c.writeto(GPS_I2CADDR, bytes([0]))
        # Do an empty write ...
        #self.reg = bytearray(1)
        # can be also written as
        # self.i2c.writeto(GPS_I2CADDR, bytes([0]))
        #self.i2c.writeto(GPS_I2CADDR, self.reg)

        from pytrack import Pytrack
        try:
            self.py = Pytrack(i2c=self.i2c)
        except OSError as oserror:
            print('OSError_1: {}'.format(oserror))
        except Exception as i2cerror:
            print('i2cerror1: {}'.format(i2cerror))

        #enable accelerometer data
        from LIS2HH12 import LIS2HH12
        try:
            self.acc = LIS2HH12(pysense=self.py)
        except OSError as oserror:
            print('OSError_2: {}'.format(oserror))
        except Exception as i2cerror:
            print('i2cerror2: {}'.format(i2cerror))

    def startGPSThread(self):
        # start thread feeding microGPS
        self.runGpsThread = True
        self.gps_thread = _thread.start_new_thread(self.feedMicroGPS,())

    def feedMicroGPS(self):
        print('Running feedMicroGPS_thread id: {}'.format(_thread.get_ident()))
        someNmeaData = ''
        while self.runGpsThread:
            gc.collect()
            # get some NMEA data
            #I2C L76 says it can read till 255 bytes
            try:
                someNmeaData = str(self.i2c.readfrom(GPS_I2CADDR, 128))
                #print(" feedMicroGPS_thread - gpsChars recieved : {}".format(len(someNmeaData)))
                #print(" NMEA data: {}".format(str(someNmeaData)))

                # Pass NMEA data to micropyGPS object
                for x in someNmeaData:
                    self.my_gps.update(str(x))
                time.sleep(10)
            except OSError as oserror:
                print(oserror)
        if not self.runGpsThread:
            try:
                _thread.exit()
            except SystemExit as sysexiterror:
                print('System Exit Error feedMicroGPS: {}'.format(sysexiterror))

    def standbyGPS(self):
        #enter standby mode for power saving
        print('standbyGPS PMTK')
        self.i2c.writeto(GPS_I2CADDR, "$PMTK161,0*28\r\n")
        #self.i2c.writeto(GPS_I2CADDR, bytes([0]))
        #Wake up only available after deep sleep

    def toggleGPS(self, on=True):
        # enable or disable back-up power to the GPS receiver
        '''
        from pytrack import Pytrack
        try:
            py = Pytrack(i2c=self.i2c)
        except OSError as oserror:
            print('OSError_: {}'.format(oserror))
        else:
            print('py.toggle_gps off')
            py.toggle_gps(on)
        '''
        print('py.toggle_gps off')
        self.py.toggle_gps(on)
        gc.collect()

    def stopGPSThread(self):
        self.runGpsThread = False

    def startPubThread(self, mqttLogic):
        # start thread feeding mqtt Pub Gps
        self.runPubThread = True
        wdt = WDT(timeout=120000)  # enable it with a timeout of 2 minutes
        self.pub_thread = _thread.start_new_thread(self.mqttPubGps,[mqttLogic, wdt])

    def mqttPubGps(self, mqttLogic, wdt):
        print('Running mqttPubGps_thread id: {}'.format(_thread.get_ident()))
        while self.runPubThread:
            if True: #if self.my_gps.fix_stat:
                if self.my_gps.fix_stat:
                    rtc = RTC()
                    if not rtc.synced():
                        gps_time = self.my_gps.timestamp
                        gps_date = self.my_gps.date
                        gps_year = 2000 + gps_date[2]
                        gps_seconds = int(gps_time[2])
                        #rtc.init((year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]]))
                        rtc.init((gps_year, gps_date[1], gps_date[0], gps_time[0], gps_time[1], gps_seconds))
                        self.log.debugLog("RTC: {}".format(rtc.now() if rtc.synced() else "unset"))
                '''
                #LOG:
                self.log.gpsLog("##############################################################")
                self.log.gpsLog("my_gps.parsed_sentences: {}".format(self.my_gps.parsed_sentences))
                self.log.gpsLog("my_gps.clean_sentences: {}".format(self.my_gps.clean_sentences))
                self.log.gpsLog("my_gps.crc_fails: {}".format(self.my_gps.crc_fails))
                self.log.gpsLog("my_gps.date_string: {}".format(self.my_gps.date_string("long")))
                self.log.gpsLog("my_gps.date_string: {}".format(self.my_gps.date_string()))
                self.log.gpsLog("my_gps.date: {}".format(self.my_gps.date))
                self.log.gpsLog("my_gps.timestamp: {}".format(self.my_gps.timestamp))
                # Dilution of Precision (DOP) values close to 1.0 indicate excellent quality position data
                self.log.gpsLog("my_gps.hdop: {}".format(self.my_gps.hdop))
                self.log.gpsLog("my_gps.pdop: {}".format(self.my_gps.pdop))
                self.log.gpsLog("my_gps.vdop: {}".format(self.my_gps.vdop))
                self.log.gpsLog("my_gps.valid: {}".format(self.my_gps.valid))
                self.log.gpsLog("my_gps.satellites_in_view: {}".format(self.my_gps.satellites_in_view))
                self.log.gpsLog("my_gps.satellites_in_use: {}".format(self.my_gps.satellites_in_use))
                self.log.gpsLog("my_gps.satellites_visible: {}".format(self.my_gps.satellites_visible()))
                self.log.gpsLog("my_gps.satellite_data_updated: {}".format(self.my_gps.satellite_data_updated()))
                self.log.gpsLog("my_gps.fix_stat: {}".format(self.my_gps.fix_stat))
                # Fix types can be: 1 = no fix, 2 = 2D fix, 3 = 3D fix
                self.log.gpsLog("my_gps.fix_type: {}".format(self.my_gps.fix_type))
                self.log.gpsLog("my_gps.fix_time: {}".format(self.my_gps.fix_time))
                #Returns number of millisecond since the last sentence with a valid fix was parsed. Returns 0 if no fix has been found
                self.log.gpsLog("my_gps.time_since_fix: {}".format(self.my_gps.time_since_fix()))
                self.log.gpsLog("my_gps.latitude_string: {}".format(self.my_gps.latitude_string()))
                self.log.gpsLog("my_gps.longitude_string: {}".format(self.my_gps.longitude_string()))
                self.log.gpsLog("my_gps._latitude: {}".format(self.my_gps._latitude))
                self.log.gpsLog("my_gps._longitude: {}".format(self.my_gps._longitude))
                self.log.gpsLog("my_gps.altitude: {}".format(self.my_gps.altitude))
                self.log.gpsLog("my_gps.geoid_height: {}".format(self.my_gps.geoid_height))
                self.log.gpsLog("my_gps.coord_format: {}".format(self.my_gps.coord_format))
                self.log.gpsLog("my_gps.compass_direction: {}".format(self.my_gps.compass_direction()))
                self.log.gpsLog("my_gps.speed_string: {}".format(self.my_gps.speed_string()))
                self.log.gpsLog("my_gps.speed: {}".format(self.my_gps.speed))
                self.log.gpsLog("my_gps.course: {}".format(self.my_gps.course))
                self.log.gpsLog("Free Mem: {}".format(gc.mem_free()))
                #PING:
                try:
                    mqttLogic.pingMQTT()
                except Exception as e:
                    print('GPS ping Exception: {}'.format(e))
                '''
                #PUB:
                try:
                    year, month, day, hour, minute, second, weekday, yearday = time.localtime()
                    timestamp = str('{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z'.format(year, month, day, hour, minute, second)) #"YYYY-MM-DDThh:mm:ssZ"
                except Exception as e:
                    print('GPS timestamp Exception: {}'.format(e))
                try:
                    lat = self.my_gps.latitude_string() #float
                    lon = self.my_gps.longitude_string() #float
                    alt = str(self.my_gps.altitude) #float
                    hdop = str(self.my_gps.hdop) #float
                    vdop = str(self.my_gps.vdop) #float
                    pdop = str(self.my_gps.pdop) #float
                except Exception as e:
                    print('GPS location Exception: {}'.format(e))
                try:
                    batteryLevel = str(self.py.read_battery_voltage())#integer
                except Exception as e:
                    print('batteryLevel Exception: {}'.format(e))
                try:
                    xt,yt,zt = self.acc.acceleration()
                    x = str(xt)
                    y = str(yt)
                    z = str(zt)
                    #print('x,y,z: {}, {}, {}'.format(x,y,z))
                    #accelerometer = str(self.acc.acceleration())
                    #print('accelerometer: {}'.format(accelerometer))
                except Exception as e:
                    print('accelerometer Exception: {}'.format(e))
                try:
                    statusMsg = '{"timestamp":"' + timestamp + '","location":{"lat":' + lat + ',"lon":' + lon + ',"alt":' + alt + ',"hdop":' + hdop + ',"vdop":' + vdop + ',"pdop":' + pdop + '},"batteryLevel":' + batteryLevel + ',"sensor":{"accelerometer":"' + x + ',' + y + ',' + z + '"}}'
                    #statusMsg = '{"timestamp":"{}","location":{"lat":{},"lon":{},"alt":{},"hdop":{},"vdop":{},"pdop":{}},"batteryLevel":{}}'.format(timestamp, lat, lon, alt, hdop, vdop, pdop, batteryLevel)
                    mqttLogic.pubMQTT(topic=config.MQTT_PUB_STATUS, msg=statusMsg, retain=False, qos=0)
                except Exception as e:
                    print('GPS PUB Exception: {}'.format(e))
            else:
                self.log.gpsLog("No fix found")
            gc.collect()
            wdt.feed()
            time.sleep(config.MQTT_PUB_SR)
        if not self.runPubThread:
            try:
                _thread.exit()
            except SystemExit as sysexiterror:
                print('System Exit Error mqttPubGps: {}'.format(sysexiterror))

    def stopPubThread(self):
        self.runPubThread = False
