# V3.2 
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
import wifi, asyncio
from mdns import Server
from time import sleep
 
from lib.npDone import setNeo
from random import getrandbits
from printF import printF, printFF, printW


green = (255, 0, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
"""
import wifi
wifi.radio.hostname('bpiw')
wifi.radio.connect('Tell My Wi-Fi Love Her', 'GodIsGood!')


"""
def scanSSID(config, baseStation):
    allScannedSSID = []
    scan = wifi.radio.start_scanning_networks()
    print(scan)
    for x in scan:
        allScannedSSID.append(x.ssid)
        
    printF(allScannedSSID)
    

    # set power mode to get WiFi power-saving off (if needed)
    #wlan.config(pm = 0xa11140)

   # scanResult =  # scan for available networks
    savedSSID = config.items('global')['wlanSSID'].split(",") # get all saved SSID from config file
   
    for x in allScannedSSID: 
        for y in savedSSID:
            if y in str(x):
                wlanPass = config.items('global')['wlanPassword'].split(',')[savedSSID.index(y)]
                printFF(f"Found Saved SSID, connecting to {y} with {wlanPass}")
                return(False, y, wlanPass)
            
    else:
        printFF("No saved SSID Found, starting AP Mode")
        ssid = f"{config.items('global')['apSSID']}-{getrandbits(32)}"
        printFF(f"No Saved SSID, starting AP {ssid} with no Pass")
        return(True,ssid , 'None')     

def connectWLAN(apMode, wlanSSID, wlanPass, config):
    if apMode:
        print("staritng AP MODE")
        wifi.radio.start_ap(wlanSSID)
        import ipaddress
        wifi.radio.set_ipv4_address_ap(ipv4=ipaddress.IPv4Address('192.168.1.1'), netmask=ipaddress.IPv4Address('255.255.255.0'), gateway=ipaddress.IPv4Address('192.168.1.1'))
        wifi.radio.start_dhcp_ap()
        setNeo(blue, 200)
        return "AP mode Started"
   
    elif apMode == False:        
        try:
            #md = Server(wifi.radio)
           # md.hostname = 'ad'

            wifi.radio.connect(wlanSSID, wlanPass)
         #   print(md.hostname)

            
            if wifi.radio.connected:
                myIP = wifi.radio.ipv4_address
                printFF(myIP)
                setNeo((0,0,255), .8, 0, True)
                return myIP

        # set power mode to get WiFi power-saving off (if needed)
        #wlan.config(pm = 0xa11140)
        except Exception as e:
            printFF('connect to wifi error: ', e)
            return f"wlan cannt connect {e}"
        

def mainFunc(config, baseStation):
    #Set hostname
   # wifi.radio.hostname = config.items('global')['baseStationName']
    #wifi.radio.hostname = 'bpi123'
    #printF(wifi.radio.hostname)
   #scan for SSID and output apModeTrue/False, SSID/ pass
    apMode, wlanSSID, wlanPass = scanSSID(config, baseStation)
    #Connect to WLAN or setup AP, returns myIP address
    #connectWLAN(True, 'bpi', 's', config)

    connectWLAN(apMode, wlanSSID, wlanPass,config)
    
if __name__ == "__main__":
    from getConfig import getConfig
    config = getConfig('baseConfig.json')

    mainFunc(config,True)