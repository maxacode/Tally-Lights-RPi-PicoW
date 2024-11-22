# V3.2
# BPI Micro
## disabled         #ap.config(pm = 0xa11140)
# Scan all SSID's
# based on config file on Flash it will use the saved SSID either base/recv config
# Connect to one if its in Config File
# If none available start AP mode with default Creds
# USAGE:
# from connectToWlan import mainFunc
# myIP = mainFunc() - returns just IP of device
# mainFunc() returns myIP if connected to wifi else returns "CustomRaise" and config

# Blue On = Connected to Wifi thats in Config
# Green On = Connected to AP Mode
# Red On = Failed to connect to any wifi
import network
from gc import collect
from time import sleep
from machine import Pin
from lib.npDone import setNeo, red, green, blue, white
from random import getrandbits
from printF import printF, printFF, printW


 
def scanSSID(config, baseStation):
   #wlan = network.WLAN(network.STA_IF)
    wlan = network.WLAN()
    #wlan.network(country="US")
   # network.hostname("tallybase")
    network.hostname(config.items('global')['baseStationName'])
    wlan.active(True)


    # set power mode to get WiFi power-saving off (if needed)
    #wlan.config(pm = 0xa11140)

   # scanResult =  # scan for available networks
    savedSSID = config.items('global')['wlanSSID'].split(",") # get all saved SSID from config file

    for x in wlan.scan(): 
        for y in savedSSID:
            if y in str(x):
                printF(f"Found Saved SSID, connecting to {y}")
                wlanPass = config.items('global')['wlanPassword'].split(',')[savedSSID.index(y)]
                collect()
                return(False, y, wlanPass)              
    else:
        printF("No saved SSID Found, starting AP Mode")
        collect()
        ssid = f"{config.items('global')['apSSID']}-{getrandbits(32)}"
        collect()
        return(True,ssid , config.items('global')['apPassword'])     

def connectWLAN(apMode, wlanSSID, wlanPass, config):
    #printF(apMode, wlanSSID, wlanPass)
    if apMode:
        # Create a WLAN object for AP mode
        ap = network.WLAN(network.AP_IF)
        # Configure AP settings
        ap.config(ssid=wlanSSID)  # Set SSID and password

       #ap.config(essid=wlanSSID, password=wlanPass)  # Set SSID and password
        # Activate AP modef
        ap.active(True)
        # set power mode to get WiFi power-saving off (if needed)
        #ap.config(pm = 0xa11140)
        # Wait until AP is active
        while not ap.active():
            sleep(1)
            
        printF("Access Point active with IP:", ap.ifconfig())
        setNeo(blue, 200)
        # Display AP's IP configuration
        collect()
        return(ap.ifconfig()[0])

    elif apMode == False:        
        wlan = network.WLAN(network.STA_IF)
        #wlan.config(hostname="tallybase2")
        network.hostname(config.items('global')['baseStationName'])
        wlan.active(True)
        # set power mode to get WiFi power-saving off (if needed)
        #wlan.config(pm = 0xa11140)

        wlan.connect(wlanSSID, wlanPass)
        #print(f'myIP = {str(wlan.ifconfig()[0])}')

        #wait for connect or fail
        if wlan.isconnected() == False:
            while 20 > 0:
                printF(wlan.status())
                setNeo(green, 0)
                if wlan.status() < 0 or wlan.status() >= 3:
                    break
                #printF('waiting for WLAN Connection... ')
                setNeo(green, 200)
                sleep(1)

        # Handle connection error
        if wlan.status() != 1010:
            setNeo(red, 200)
            return('customRaise: network connection failed')
            
        setNeo(white, 200)
        return (wlan.ifconfig()[0])

def mainFunc(config, baseStation):
        
    apMode, wlanSSID, wlanPass = scanSSID(config, baseStation)
    collect()
    return(connectWLAN(apMode, wlanSSID, wlanPass,config))
    
if __name__ == "__main__":
    from getConfig import getConf
    config = getConf('baseConfig.json')
    print(config.items('global')['baseStationName'])
    mainFunc(config, True)