
import os
import machine
from machine import UART
from machine import SD
import utime
import state

uart = UART(0, baudrate=115200)
os.dupterm(uart)

class Logger:

    def __init__(self, path='/sd/logs/', mode='a'):
        self.path = path
        self.mode = mode
        self.bootLogFile = 'boot.log'
        self.debugLogFile = 'debug.log'
        self.gpsLogFile = 'gps.log'

    def bootLog(self, message, p=True):
        try:
            log = '{}: {}'.format(utime.ticks_ms(), message)
            if p:
                print('Boot Log: ' + log)
            if state.LOGGER_ACTIVE:
                #'r' 	Open a file for reading. (default)
                #'w' 	Open a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
                #'x' 	Open a file for exclusive creation. If the file already exists, the operation fails.
                #'a' 	Open for appending at the end of the file without truncating it. Creates a new file if it does not exist.
                #'t' 	Open in text mode. (default)
                #'b' 	Open in binary mode.
                #'+' 	Open a file for updating (reading and writing)
                with open(self.path + self.bootLogFile, self.mode) as f:
                    f.write(log + "\r\n")
        except IOError as ioerror:
            try:
                if ioerror.errno == errno.ENOENT:
                    print('Exception Logger.bootLog IOError.ENOENT - file does not exist: {}'.format(ioerror))
                elif ioerror.errno == errno.EACCES:
                    print('Exception Logger.bootLog IOError.EACCES - cannot be read: {}'.format(ioerror))
                else:
                    print('Exception Logger.bootLog IOError: {}'.format(ioerror))
            except AttributeError as atterr:
                print('Exception Logger.bootLog IOError AttributeError: {}'.format(atterr))
        except OSError as oserror:
            try:
                if oserror.errno == errno.ENOENT:
                    print('Exception Logger.bootLog OSError.ENOENT - file does not exist: {}'.format(oserror))
                else:
                    print('Exception Logger.bootLog OSError: {}'.format(oserror))
            except AttributeError as atterr:
                print('Exception Logger.bootLog IOError AttributeError: {}'.format(atterr))
        except Exception as e:
            print('Exception Logger.bootLog Exception: {}'.format(e))

    def debugLog(self, message, p=True):
        try:
            log = '{}: {}'.format(utime.ticks_ms(), message)
            if p:
                print('Debug Log: ' + log)
            if state.LOGGER_ACTIVE:
                with open(self.path + self.debugLogFile, self.mode) as f:
                    f.write(log + "\r\n")
                #f=open(self.path + self.debugLogFile, self.mode)
                #f.write(log + "\r\n")
        except IOError as ioerror:
            try:
                if ioerror.errno == errno.ENOENT:
                    print('Exception Logger.debugLog IOError.ENOENT - file does not exist: {}'.format(ioerror))
                elif ioerror.errno == errno.EACCES:
                    print('Exception Logger.debugLog IOError.EACCES - cannot be read: {}'.format(ioerror))
                else:
                    print('Exception Logger.debugLog IOError: {}'.format(ioerror))
            except AttributeError as atterr:
                print('Exception Logger.debugLog IOError AttributeError: {}'.format(atterr))
        except OSError as oserror:
            try:
                if oserror.errno == errno.ENOENT:
                    print('Exception Logger.debugLog OSError.ENOENT - file does not exist: {}'.format(oserror))
                else:
                    print('Exception Logger.debugLog OSError: {}'.format(oserror))
            except AttributeError as atterr:
                print('Exception Logger.debugLog IOError AttributeError: {}'.format(atterr))
        except Exception as e:
            print('Exception Logger.debugLog Exception: {}'.format(e))

    def gpsLog(self, message, p=True):
        log = '{}: {}'.format(utime.ticks_ms(), message)
        if p:
            print('GPS Log: ' + log)
        if state.LOGGER_ACTIVE:
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
