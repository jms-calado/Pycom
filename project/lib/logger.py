
import os
import machine
from machine import UART
from machine import SD
import utime

uart = UART(0, baudrate=115200)
os.dupterm(uart)

active = False

class Logger:

    def __init__(self, path='/sd/logs/', mode='a'):
        self.path = path
        self.mode = mode
        self.bootLogFile = 'boot.log'
        self.debugLogFile = 'debug.log'
        self.gpsLogFile = 'gps.log'

    def bootLog(self, message, p=True):
        log = '{}: {}'.format(utime.ticks_ms(), message)
        if p:
            print('Boot Log: ' + log)
        if active:
            #'r' 	Open a file for reading. (default)
            #'w' 	Open a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
            #'x' 	Open a file for exclusive creation. If the file already exists, the operation fails.
            #'a' 	Open for appending at the end of the file without truncating it. Creates a new file if it does not exist.
            #'t' 	Open in text mode. (default)
            #'b' 	Open in binary mode.
            #'+' 	Open a file for updating (reading and writing)
            with open(self.path + self.bootLogFile, self.mode) as f:
                f.write(log + "\r\n")

    def debugLog(self, message, p=True):
        log = '{}: {}'.format(utime.ticks_ms(), message)
        if p:
            print('Debug Log: ' + log)
        if active:
            with open(self.path + self.debugLogFile, self.mode) as f:
                f.write(log + "\r\n")

    def gpsLog(self, message, p=True):
        log = '{}: {}'.format(utime.ticks_ms(), message)
        if p:
            print('GPS Log: ' + log)
        if active:
            with open(self.path + self.gpsLogFile, self.mode) as f:
                f.write(log + "\r\n")

    def printBootLog(self):
        print('=== Printing Boot Log ===')
        with open(self.path + self.bootLogFile, 'r') as f:
            print(f.read())
        print('=== END Print Boot Log ===')

    def printDebugLog(self):
        print('=== Printing Debug Log ===')
        with open(self.path + self.debugLogFile, 'r') as f:
            print(f.read())
        print('=== END Print Debug Log ===')

    def printGpsLog(self):
        print('=== Printing GPS Log ===')
        with open(self.path + self.gpsLogFile, 'r') as f:
            print(f.read())
        print('=== END Print GPS Log ===')

    def resetBootLog(self):
        print('WARNING: Removing Boot Log File')
        try:
            os.remove(self.path + self.bootLogFile)
        except Exception as resetBootError:
            print('Reset Boot File Error: {}'.format(resetBootError))

    def resetDebugLog(self):
        print('WARNING: Removing Debug Log File')
        try:
            os.remove(self.path + self.debugLogFile)
        except Exception as resetDebugError:
            print('Reset Debug File Error: {}'.format(resetDebugError))

    def resetGpsLog(self):
        print('WARNING: Removing GPS Log File')
        try:
            os.remove(self.path + self.gpsLogFile)
        except Exception as resetGpsError:
            print('Reset GPS File Error: {}'.format(resetGpsError))
