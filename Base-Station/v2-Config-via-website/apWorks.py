

import network
import time
print("apWorks V 2.8")

# Function to configure the ESP in AP mode
def setup_ap(ssid,password,hostName):
    # Create a WLAN object for AP mode
    ap = network.WLAN(network.AP_IF)
    # Configure AP settings
    ap.config(essid=ssid, password=password)  # Set SSID and password
    # Activate AP modef
    ap.active(True)
    network.hostname(hostName)
    # Wait until AP is active
    while not ap.active():
        time.sleep(1)
    
    # Display AP's IP configuration
    print("Access Point active with IP:", ap.ifconfig())

 

# Set up the ESP in AP mode
#setup_ap(ssid,password,hostname)
 
