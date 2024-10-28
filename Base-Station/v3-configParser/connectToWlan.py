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

led = Pin("LED", Pin.OUT)
led.value(1)



# var for each section mappings
globalMap = 'global'
#print("Starting WLAN Connection")
 
def flashLed(times,duration,msg):
    x = 0
    while x < times:
        time.sleep(duration)
        #print(msg, " ", time.time())
        x += 1
        led.toggle()
        time.sleep(duration)
        
        
def scanSSID(config):
   # wlan = network.WLAN(network.STA_IF)
    from network import WLAN
    wlan = network.WLAN()
    wlan.active(True)
    scanResult = wlan.scan()
    savedSSID = config.items('global')['wlanSSID'].split(",")
    #print(savedSSID)
   # print(scanResult)
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
        wlanSSID = config[globalMap]['apSSID']
        wlanPass = config[globalMap]['apPassword']
        return(True, wlanSSID, wlanPass)
        
        

    
def connectWLAN(apMode, wlanSSID, wlanPass,config):
    if apMode:
        # Create a WLAN object for AP mode
        ap = network.WLAN(network.AP_IF)
        # Configure AP settings
        ap.config(essid=wlanSSID, password=wlanPass)  # Set SSID and password
        # Activate AP modef
        ap.active(True)
        network.hostname(config[globalMap]["baseStationName"])
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
    
    apMode, wlanSSID, wlanPass = scanSSID(config)
   # 3wlanSSID = config[globalMap]['wlanSSID'][0]
    #wlanPass = config[globalMap]['wlanPassword'][0]
   # apMode = False
    # Returns baseIP in AP or Station mode
    return(connectWLAN(apMode, wlanSSID, wlanPass,config))
    
if __name__ == "__main__":
    print(mainFunc())