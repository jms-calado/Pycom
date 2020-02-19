#source: https://core-electronics.com.au/tutorials/pycom-gpy-getting-started.html
import time
from network import LTE
from machine import Timer
from logger import Logger
import state
import config

# Need to use global variables.
# If in each function you delare a new reference, functionality is broken
#lte = LTE()
#enable logger
log = Logger()

# Disable LTE modem
def disableLTE(lte):
    try:
        lte.deinit(detach=True, reset=True)
        log.debugLog('LTE disabled')
    except Exception as lteError:
        log.debugLog("lteError: {}".format(lteError))

# Returns a network.LTE object with an active Internet connection.
def getLTE(lte):
    # If already used, the lte device will have an active connection.
    # If not, need to set up a new connection.
    if lte.isconnected():
        return lte
    # If correctly configured for carrier network, attach() should succeed.
    if not lte.isattached():
        print("Attaching to LTE network ", end='')
        log.debugLog("Attaching to LTE network ", p=False)
        # start a timer
        chrono = Timer.Chrono()
        chrono.start()
        try:
            lte.attach(band = 20, apn = config.LTENB_APN)
        except Exception as e:
            log.debugLog("lte.attach error: {}".format(e))
        while(chrono.read() < 30): #wait 30 sec for lte attached
            if lte.isattached():
                print(" LTE attached OK")
                log.debugLog(" LTE attached OK", p=False)
                break
            print('.', end='')
            time.sleep(1)
        if not lte.isattached():
            return lte
    # Once attached, connect() should succeed.
    if not lte.isconnected():
        print("Connecting on LTE network ", end='')
        log.debugLog("Connecting on LTE network ", p=False)
        try:
            lte.connect()
        except Exception as e:
            log.debugLog("lte.connect error: {}".format(e))
        while(chrono.read() < 30): #wait 30 sec for lte connected
            if lte.isconnected():
                print(" LTE connected OK")
                log.debugLog(" LTE connected OK", p=False)
                break
            print('.', end='')
            time.sleep(1)
        if not lte.isconnected():
            return lte
    # Once connect() succeeds, any call requiring Internet access will
    # use the active LTE connection.
    return lte

# Clean disconnection of the LTE network is required for future
# successful connections without a complete power cycle between.
def endLTE(lte):
    state.CONNECTED = False
    log.debugLog("Disconnecting LTE ... ")
    try:
        lte.disconnect()
        log.debugLog("LTE disconnected OK")
    except Exception as lteError:
        log.debugLog("lteError Disconnecting: {}".format(lteError))
    time.sleep(1)
    log.debugLog("Detaching LTE ... ")
    try:
        lte.dettach()
        log.debugLog("LTE detached OK")
    except Exception as lteError:
        log.debugLog("lteError Detaching: {}".format(lteError))

def send_at_cmd_pretty(lte, cmd):
    response = lte.send_at_cmd(cmd).split('\r\n')
    return response

# Start LTE
def startLTE():
    try:
        lte = LTE()
    except Exception as lteError:
        log.debugLog("lte = LTE(): {}".format(lteError))
        state.CONNECTED = False
        return
    '''
    # check for a valid iccid (exception is raised if no SIM card is connected)
    try:
        iccid = lte.iccid()
        if iccid is None:
            log.debugLog('Iccid is None 1')
            time.sleep(5)
            iccid = lte.iccid()
            if iccid is None:
                log.debugLog('Iccid is None 2')
                time.sleep(5)
                iccid = send_at_cmd_pretty(lte, 'AT+SQNCCID?').split('\r\n')[1].split('"')[1]
                if iccid == '':
                    raise ValueError('Iccid is None AT')
                else:
                    log.debugLog("LTE iccid AT: {}".format(iccid))
            else:
                log.debugLog("LTE iccid 2: {}".format(iccid))
        else:
            log.debugLog("LTE iccid 1: {}".format(iccid))
    except Exception as e:
        log.debugLog("LTE iccid error: {}".format(e))
        #state.CONNECTED = False
        #return lte
    '''
    try:
        # has coverage:
        lte_coverage = lte.ue_coverage()
        log.debugLog("LTE initial coverage: {}".format(lte_coverage))
        for counter in range(3): #repeat getLTE at most 3 times
            lte = getLTE(lte)
            if lte.isconnected():
                state.CONNECTED = True
                break
    except Exception as e:
        log.debugLog("getLTE error: {}".format(e))
    '''finally:
        self.endLTE(lte)
        log.debugLog('end lte')
    '''
    try:
        # Query AT
        log.debugLog('Query AT')
        lte.pppsuspend()
        '''
            showphy = send_at_cmd_pretty(lte, 'AT!="showphy"')
            for line in showphy:
                log.debugLog(line)
            fsm = send_at_cmd_pretty(lte, 'AT!="fsm"')
            for line in fsm:
                log.debugLog(line)
        '''
        atCSQ = send_at_cmd_pretty(lte, 'AT+CSQ')
        log.debugLog(atCSQ)
        atCEREG = send_at_cmd_pretty(lte, 'AT+CEREG?')
        log.debugLog(atCEREG)
        lte.pppresume()
        log.debugLog('end AT')
    except Exception as e:
        log.debugLog("Query AT error: {}".format(e))
    return lte
