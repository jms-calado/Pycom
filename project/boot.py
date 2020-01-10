import os
import machine
from machine import UART, SD
import gc
import pycom
import time
import utime
from network import WLAN, Server, Bluetooth, LTE
from logger import Logger
from pytrack import Pytrack
from LIS2HH12 import LIS2HH12
import state

start = utime.ticks_us()

# enable logger
log = Logger()

# enable GC
gc.enable()

uart = UART(0, baudrate=115200)
os.dupterm(uart)
'''
print('Wait 10')
time.sleep(10)
print('Wait 10 over')
'''
pwake_log = None
psleep_left_log = None
'''
try:
    py = Pytrack()
    # display the reset reason code and the sleep remaining in seconds
    # possible values of wakeup reason are:
    # WAKE_REASON_ACCELEROMETER = 1
    # WAKE_REASON_PUSH_BUTTON = 2
    # WAKE_REASON_TIMER = 4
    # WAKE_REASON_INT_PIN = 8
    pwake_log = py.get_wake_reason()
    psleep_left_log = py.get_sleep_remaining()
except Exception as i2c_error:
    print('I2C error: {}'.format(i2c_error))
'''
'''
# Machine Reset Causes:
# machine.PWRON_RESET,
# machine.HARD_RESET,
# machine.WDT_RESET,
# machine.DEEPSLEEP_RESET,
# machine.SOFT_RESET,
# machine.BROWN_OUT_RESET
'''
mwake_log = machine.wake_reason()
reset_log = machine.reset_cause()
mrst_log = machine.remaining_sleep_time()

#SD mount
try:
    sd = SD()
    os.mount(sd, '/sd')
except Exception as sdError:
    print("SD mount Error: {}".format(sdError))
    state.LOGGER_ACTIVE = False
else:
    state.LOGGER_ACTIVE = True
    log.bootLog('New boot')
    log.bootLog('Wakeup reason (machine): {} / Reset reason: {} / Remaining sleep time {}'.format(mwake_log, reset_log, mrst_log))
    log.bootLog('Wakeup reason (pycoproc): {} / Aproximate sleep remaining: {}  sec'.format(pwake_log, psleep_left_log))

# Read/Set number of Boots
try:
    bootNum = pycom.nvs_get('bootNum')
except Exception as nvserror:
    bootNum = None
    log.debugLog('Boot nvserror: {}'.format(nvserror))
if bootNum == None:
    bootNum = 0
pycom.nvs_set('bootNum', bootNum + 1)
log.debugLog('bootNum: {}'.format(bootNum))

# enable WDT on boot
if not pycom.wdt_on_boot():
    try:
        pycom.wdt_on_boot(True)
        pycom.wdt_on_boot_timeout(300000) # 5 minutes = 300000 ms
        log.bootLog('WDT on boot enabled')
    except Exception as wdtBootError:
        log.bootLog("WDT on boot Error: {}".format(wdtBootError))
else:
    log.bootLog('WDT on boot enabled')

# Disable WLAN
if pycom.wifi_on_boot():
    try:
        wlan = WLAN()
        wlan.deinit()
        log.bootLog('WLAN disabled')
    except Exception as wlanError:
        log.bootLog("wlanError: {}".format(wlanError))
    pycom.wifi_on_boot(False)
else:
    log.bootLog('WLAN disabled')

# Disable Server
try:
    server = Server()
    if (server.isrunning()):
        server.deinit()
    log.bootLog('Server disabled')
except Exception as serverError:
    log.bootLog("serverError: {}".format(serverError))

# Disable BLE
try:
    bluetooth = Bluetooth()
    bluetooth.deinit()
    log.bootLog('Bluetooth disabled')
except Exception as bluetoothError:
    log.bootLog("bluetoothError: {}".format(bluetoothError))

# Disable LTE
try:
    lte = LTE()
    lte.deinit(detach=True, reset=True)
    log.bootLog('LTE disabled')
except Exception as lteError:
    log.bootLog("lteError: {}".format(lteError))

gc.collect()

machine.main('main.py')

end = utime.ticks_us()
#took = end - start
log.bootLog("boot.py executed in: {} uSec".format(end - start))
