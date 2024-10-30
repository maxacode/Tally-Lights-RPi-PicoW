#network library
#pico W
# V1.0 done
# connect to SSID up to 10 attempts then fails.
#USAGE:
# import connectToWlan
# connectToWlan.connectWLAN() - thats it

# Fash Flash - Infinite = NOT CONNECTED
# Slower FLash - 5 times then Solid = CONNECTED

print("Starting Up Device")

import network
import time
from machine import Pin
from npDone import setNeo
import random

green = (255, 0, 0)
orange = (100, 200, 0)
yellow = (255, 230, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
violet = (0, 255, 100)

setNeo(red,50)

# var for each section mappings
globalMap = 'global'
#print("Starting WLAN Connection")




unique_id = random.getrandbits(32)

def scanSSID(config, baseStation):
   # wlan = network.WLAN(network.STA_IF)
    from network import WLAN
    wlan = network.WLAN()
    wlan.active(True)
    scanResult = wlan.scan()
    savedSSID = config.items('global')['wlanSSID'].split(",")

    for x in scanResult: 
        for y in savedSSID:
           # print(y)
            if y in str(x):
                print(f"Found Saved SSID, connecting to {y}")
                wlanSSID = y
               # print(wlanSSID)
                wlanPass = config.items('global')['wlanPassword'].split(',')[savedSSID.index(y)]
                
               # print('ssid: ', wlanSSID,'pass: ',  wlanPass)
                return(False, wlanSSID, wlanPass)
                
    else:
        print("No saved SSID Found, starting AP Mode")
        wlanSSID = str(config.items(globalMap)['apSSID']) + " - " + str(unique_id)
        print(wlanSSID)
        wlanPass = config.items(globalMap)['apPassword']
        return(True, wlanSSID, wlanPass)
        
        

    
def connectWLAN(apMode, wlanSSID, wlanPass, config):
    if apMode:
        # Create a WLAN object for AP mode
        ap = network.WLAN(network.AP_IF)
        # Configure AP settings
        ap.config(essid=wlanSSID, password=wlanPass)  # Set SSID and password
        # Activate AP modef
        ap.active(True)
        network.hostname(config.items(globalMap)["baseStationName"])
        # Wait until AP is active
        while not ap.active():
            time.sleep(1)
            
        print("Access Point active with IP:", ap.ifconfig())
        # Display AP's IP configuration
        return(ap.ifconfig()[0])

    elif apMode == False:        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPass)
        #wait for connect or fail
        max_wait = 100
        while max_wait > 0:
           # print(wlan.status())
            led.toggle()
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('waiting for WLAN Connection... ', max_wait)
            time.sleep(2)
        
        # Handle connection error
        if wlan.status() != 3:
            flashLed(9999, 0.1,'Failed to connect to WLAN')
            status = ('customRaise: network connection failed')
            
        else:
           # print('Connected')
            status = wlan.ifconfig()
            wlanStatus = status[0]
            print( f'ip = {str(status)}')
                    

    return (wlanStatus)

def mainFunc(configFileName):
    from getConfig import getConf
    config = getConf(configFileName)
    if 'recvConfig' in configFileName:
        baseStation = False
    elif "baseConfig" in configFileName:
        baseStation = True
    else:
        print("Error")
        
    apMode, wlanSSID, wlanPass = scanSSID(config, baseStation)

    return(connectWLAN(apMode, wlanSSID, wlanPass,config))
    
if __name__ == "__main__":
    import os
    if "recvConfig" in str(os.listdir()):
        print('reiver')
        print(mainFunc('recvConfig.json'))
        
    elif "baseConfig" in str(os.listdir()):
        print("base")
        print(mainFunc('baseConfig.json'))
    else:
        print("No config file found")