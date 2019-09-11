import time
from machine import RTC, Timer
from logger import Logger
import config

#enable logger
log = Logger()

NTP_SERVER = config.NTP_SERVER

# Sets the internal real-time clock.
# Needs LTE for Internet access.
def setRTC(rtc):
    print("Updating RTC from {} ".format(NTP_SERVER), end='')
    log.debugLog("Updating RTC from {} ".format(NTP_SERVER), p=False)
    # start a timer
    chrono = Timer.Chrono()
    chrono.start()
    rtc.ntp_sync(NTP_SERVER)
    while not rtc.synced():
        if chrono.read() > 20: #wait 20 sec for RTC sync
            print(' RTC update failed')
            log.debugLog(' RTC update failed', p=False)
            break
        print('.', end='')
        time.sleep(1)
    if rtc.synced():
        print(' RTC updated OK')
        log.debugLog(' RTC updated OK', p=False)

# Only returns an RTC object that has already been synchronised with an NTP server.
def getRTC(rtc):
    if not rtc.synced():
        for counter in range(3): #repeat setRTC at most 3 times
            setRTC(rtc)
            if rtc.synced():
                break
    return rtc
