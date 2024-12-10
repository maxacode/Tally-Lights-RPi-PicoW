# v6.4  Recivers connectTowLan.py VSCode
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

6.5
- removed scannSSID and generating AP mode.
- only connects to saved SSID of Tally
- connectWLAN only takes SSID and Config object and returns only IP address.
- main only returns Config object now


6.4 testing PM
        wlan.config(pm=wlan.PM_NONE)



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

def connectWLAN(wlanSSID:str, config: object) -> tuple[bool, str]:        
    """
    Connect to WLAN based on passed Params

    Params:
        wlanSSID: SSID to connect
        config: config file Object

    Returns:
        ipAddress:
  """
    printF(f'Connecting to {wlanSSID}')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    # set power mode to get WiFi power-saving off (if needed)
    #wlan.config(pm = network.WLAN.PM_NONE)
    #wlan.config(pm = 0x111022)
    #wlan.config(pm=0)
    wlan.config(pm=wlan.PM_NONE)

    #wait for connect or fail
    while 200 > 0:
        wlan.connect(wlanSSID)

        setNeo(white, 0)
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        printF('waiting for WLAN Connection... ', wlan.status())
        setNeo(white, int(config.items('tallyBrightness')['white']))
        sleep(1)

    # Handle connection error
#     if wlan.status() != 3:
#         setNeo(red, int(config.items('tallyBrightness')['red']))
#         return('customRaise: network connection failed')
        
    #else:
    return (str(wlan.ifconfig()[0]))

def mainFunc(config: object) -> tuple[bool, str]:  
    """
    Main Function to Scan SSIDs and connect to it

    Params:
        config: config file Object
        baseStation: True if baseStation

    Returns:
        tuple:
            apMode, myIP ex: (True, '192.168.88.23'
    """

    #apMode, wlanSSID, wlanPass = scanSSID(config, baseStation)
   # collect()
   
    wlanSSID = f"{config.items('global')['wlanSSID']}" #type: ignore

   
    myIP = connectWLAN(wlanSSID,config)
    #print(myIP)
    return myIP
    
if __name__ == "__main__":
    
    from getConfig import getConf
    config = getConf('recvConfig.json')
   # print(f'MDNS: ',config.items('global')['baseStationName']) #type: ignore
    mainFunc(config)



