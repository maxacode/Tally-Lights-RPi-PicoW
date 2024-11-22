# v6.3  Recivers connectTowLan.py VSCode
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

import network #type: ignore
from gc import collect #type: ignore
from time import sleep
from machine import Pin #type: ignore
from random import getrandbits
from json import loads

# my Libs
from lib.neopixel.npDone import setNeo, red, green, blue, white, off #type: ignore
from lib.printF import printF, printFF, printW #type: ignore


def scanSSID(config: object, baseStation: bool) -> tuple[bool, str, str]:
    """
    Scan for available SSID's
    If SSID is in config file connect to it
    If not start AP mode

    Params: 
        config: config file Object
        baseStation: True if baseStation
    Returns: 
        tuple: 
         apMode, wlanSSID, wlanPass ex: (True, 'AP-1234', '') or (False, 'SSID', 'Password')
    """
   #wlan = network.WLAN(network.STA_IF)
    
    wlan = network.WLAN()
    wlan.active(False)
    wlan.active(True)
   # wlan.config(pm = network.WLAN.PM_NONE)
    wlan.config(pm = 0x111022)

    # set power mode to get WiFi power-saving off (if needed)
    #wlan.config(pm = 0xa11140) 

   # scanResult =  # scan for available networks
    savedSSID: str = config.items('global')['wlanSSID'].split(",") # get all saved SSID from config file #type: ignore
    scan = wlan.scan()
    ssids: list[str] = []
        
    for entry in scan:
        ssid, _, _, _, _, _ = entry
        ssids.append(ssid.decode('utf-8'))  # Decode the SSID from bytes to string
   
    apSSID = config.items('global')['apSSID'] #type: ignore
    
    if apSSID in scan:
        printFF(f"AP Found connecting to {apSSID}")
        return(False, apSSID, '') # '' empty password, tested and works
    
    for x in ssids:
        for y in savedSSID:
            if y in x:
                printFF(f"Found Saved SSID, connecting to {y}")
                wlanPass: str = config.items('global')['wlanPassword'].split(',')[savedSSID.index(y)] #type: ignore
                return(False, y, wlanPass)              
    else:
        collect()
        ssid = f"{config.items('global')['apSSID']}-{getrandbits(32)}" #type: ignore
        printFF("No saved SSID Found, starting AP Mode no Password", ssid)
        return(True,ssid , '')     

def connectWLAN(apMode: bool, wlanSSID:str, wlanPass:str, config: object) -> tuple[bool, str]:        
    """
    Connect to WLAN based on passed Params

    Params:
        apMode: True if AP mode
        wlanSSID: SSID to connect
        wlanPass: Password to connect
        config: config file Object

    Returns:
        tuple:
            apMode, myIP ex: (True, '192.168.88.2')
    """
    if apMode:
        # Create a WLAN object for AP mode
        ap = network.WLAN(network.AP_IF)
        # Configure AP settings
        ap.config(ssid= wlanSSID, security = 0)
      #  ap.config(ssid=wlanSSID, key = wlanPass)  # Set SSID and password
        # Activate AP modef
        ap.active(True)
        # set power mode to get WiFi power-saving off (if needed)
        ap.config(pm = network.WLAN.PM_NONE)
        # Wait until AP is active
        while not ap.active():
            sleep(1)
            
        printF("Access Point active with IP:", ap.ifconfig())
        setNeo(blue, int(config.items('tallyBrightness')['blue']))
        # Display AP's IP configuration
        collect()
        return(apMode, str(ap.ifconfig()[0]))

    elif apMode == False:        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        wlan.active(True)
        # set power mode to get WiFi power-saving off (if needed)
        #wlan.config(pm = network.WLAN.PM_NONE)
        wlan.config(pm = 0x111022)

        wlan.connect(wlanSSID, wlanPass)
        #wait for connect or fail
        while 20 > 0:
            setNeo(white, 0)
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            printF('waiting for WLAN Connection... ', wlan.status())
            setNeo(white, int(config.items('tallyBrightness')['white']))
            sleep(1)

        collect()
        # Handle connection error
        if wlan.status() != 3:
            setNeo(red, int(config.items('tallyBrightness')['red']))
            return(apMode, 'customRaise: network connection failed')
            
        else:
            return (apMode, str(wlan.ifconfig()[0]))

def mainFunc(config: object, baseStation: bool) -> tuple[bool, str]:  
    """
    Main Function to Scan SSIDs and connect to it

    Params:
        config: config file Object
        baseStation: True if baseStation

    Returns:
        tuple:
            apMode, myIP ex: (True, '192.168.88.23'
    """

    apMode, wlanSSID, wlanPass = scanSSID(config, baseStation)
    collect()
    apMode, myIP = connectWLAN(apMode, wlanSSID, wlanPass,config)
    print( apMode, myIP)
    return apMode, myIP
    
if __name__ == "__main__":
    
    from getConfig import getConf
    config = getConf('recvConfig.json')
   # print(f'MDNS: ',config.items('global')['baseStationName']) #type: ignore
    mainFunc(config, False)



