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
    #print("Disconnecting LTE ... ", end='')
    log.debugLog("Disconnecting LTE ... ")
    lte.disconnect()
    #print("LTE disconnected OK")
    log.debugLog("LTE disconnected OK")
    time.sleep(1)
    #print("Detaching LTE ... ", end='')
    log.debugLog("Detaching LTE ... ")
    lte.dettach()
    #print("LTE detached OK")
    log.debugLog("LTE detached OK")

def send_at_cmd_pretty(lte, cmd):
    response = lte.send_at_cmd(cmd, delay=1000).split('\r\n')
    return response

# Start LTE
def startLTE():
    lte = LTE()
    # check for a valid iccid (exception is raised if no SIM card is connected)
    try:
        iccid = lte.iccid()
        if iccid is None:
            time.sleep(5)
            iccid = lte.iccid()
            if iccid is None:
                raise ValueError('Iccid is None')
            else:
                log.debugLog("LTE iccid retry: {}".format(iccid))
        else:
            log.debugLog("LTE iccid: {}".format(iccid))
    except Exception as e:
        log.debugLog("LTE iccid error: {}".format(e))
        state.CONNECTED = False
        return lte
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
        log.debugLog("startLTE error: {}".format(e))
    '''finally:
        self.endLTE(lte)
        log.debugLog('end lte')
    '''
    try:
        # Query AT
        log.debugLog('Query AT')
        lte.pppsuspend()
        showphy = send_at_cmd_pretty(lte, 'AT!="showphy"')
        for line in showphy:
            log.debugLog(line)
        fsm = send_at_cmd_pretty(lte, 'AT!="fsm"')
        for line in fsm:
            log.debugLog(line)
        atCSQ = send_at_cmd_pretty(lte, 'AT+CSQ')
        log.debugLog(atCSQ)
        atCEREG = send_at_cmd_pretty(lte, 'AT+CEREG?')
        log.debugLog(atCEREG)
        lte.pppresume()
        log.debugLog('end AT')
    except Exception as e:
        log.debugLog("Query AT error: {}".format(e))
    return lte
