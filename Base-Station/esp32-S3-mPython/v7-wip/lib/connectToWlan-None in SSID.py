# V3.3 - VSCode baseStation connectTowLan.py
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
"""
Default power management mode
CYW43_DEFAULT_PM = 0xA11142

Aggressive power management mode for optimal power usage at the cost of performance
CYW43_AGGRESSIVE_PM = 0xA11C82

Performance power management mode where more power is used to increase performance
CYW43_PERFORMANCE_PM = 0x111022

    #wlan.config(pm = 0xa11140) usualy one used
        wlan.config(pm = 0xA11C82)

    0xA11C82
    
    PM_PERFORMANCE: enable WiFi power management to balance power savings and WiFi performance

PM_POWERSAVE: enable WiFi power management with additional power savings and reduced WiFi performance

PM_NONE: disable wifi power management

    wlan.config(pm = network.WLAN.PM_NONE)
    #wlan.config(pm = 0x111022)
"""

import network
from gc import collect
from time import sleep
from machine import Pin
from lib.npDone import setNeo, red, green, blue, white
from random import getrandbits
from printF import printF, printFF, printW


 
def scanSSID(config: object, baseStation: bool) -> tuple:
    """
    Scans for available SSID's and returns the SSID to connect to
    Params:
        config (object): ConfigParser object
        baseStation (bool): True if Base Station, False if Receiver
    Returns:    
        tuple: (apMode: bool, wlanSSID, wlanPass)
    """
    
    wlan = network.WLAN()
    wlan.active(True)
   # wlan.config(pm = network.WLAN.PM_NONE)
    wlan.config(pm = network.WLAN.PM_PERFORMANCE)


    # set power mode to get WiFi power-saving off (if needed)
    #wlan.config(pm = 0xa11140) 

   # scanResult =  # scan for available networks
    savedSSID: list = config.items('global')['wlanSSID'].split(",") # get all saved SSID from config file
    if "None" not in savedSSID:
        scan: list = wlan.scan()
     
        ssids: list = []
        for entry in scan:
            ssid, _, _, _, _, _ = entry
            ssids.append(ssid.decode('utf-8'))  # Decode the SSID from bytes to string
     
        for x in ssids:
            for y in savedSSID:
                if y in x:
                    printFF(f"Found Saved SSID, connecting to {y}")
                    wlanPass: str = config.items('global')['wlanPassword'].split(',')[savedSSID.index(y)]
                    return(False, y, wlanPass)

    else:
        ssid: str = f"{config.items('general')['apSSID']}"
        printFF("No saved SSID Found, starting AP Mode no Password", ssid)
        return(True,ssid , '')     

def connectWLAN(apMode: bool, wlanSSID:str , wlanPass: str, config:object) -> tuple:
    """
    Connects to WLAN using Params and returns apMode/ myIP
    Params:
        apMode (bool): True if AP Mode, False if not
        wlanSSID (str): SSID to connect to
        wlanPass (str): Password to connect to SSID
        config (object): ConfigParser object
    Returns:
        tuple: (apMode, myIP)
    """
    printF(apMode, wlanSSID, wlanPass)
    if apMode:
        # Create a WLAN object for AP mode
        ap = network.WLAN(network.AP_IF)
        
        ap.active(True)

        ap.config(essid = wlanSSID, security = 0)
        ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))

        ap.config(pm = network.WLAN.PM_NONE)

        # Configure AP settings
      #  ap.config(ssid=wlanSSID, key = wlanPass)  # Set SSID and password
        # Activate AP modef
        # set power mode to get WiFi power-saving off (if needed)
        # Wait until AP is active
        while not ap.active():
            sleep(1)
            
        printF("Access Point active with IP:", ap.ifconfig())
        setNeo(blue, 200)
        # Display AP's IP configuration
        collect()
        return(apMode, ap.ifconfig()[0])
    
    
    elif apMode == False:
        wlan = network.WLAN(network.STA_IF)
        #wlan.config(hostname="tallybase2")
        network.hostname(config.items('global')['baseStationName'])
        #wlan.config(pm = network.WLAN.PM_NONE)
        wlan.config(pm = network.WLAN.PM_PERFORMANCE)

        wlan.active(True)
        # set power mode to get WiFi power-saving off (if needed)

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
            return(apMode, 'customRaise: network connection failed')
            
        setNeo(white, 200)
        return (apMode, wlan.ifconfig()[0])

def mainFunc(config: object, baseStation: bool) -> tuple:
    """
    Main function to connect to WLAN
    Params:
        config (object): ConfigParser object
        baseStation (bool): True if Base Station, False if Receiver
    Returns:
        tuple: (apMode, myIP)
    #TODO: Why is baseStation being passed in? It is already in the config file name
    """
        
    apMode, wlanSSID, wlanPass = scanSSID(config, baseStation)
    collect()
    apMode, myIP = connectWLAN(apMode, wlanSSID, wlanPass,config)
    print( apMode, myIP)
    return apMode, myIP

if __name__ == "__main__":
    from getConfig import getConf
    config = getConf('baseConfig.json')
    print(config.items('global')['baseStationName'])
    mainFunc(config, True)
