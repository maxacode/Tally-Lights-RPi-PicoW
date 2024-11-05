

import network
import time
print("v2.7")

# Function to configure the ESP in AP mode
def setup_ap():
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

 
# SSID and password for the Access Point
 
ssid = "Tally-Lights"
password = "LSDkj%$#8ew7lka4"
hostName = "Tally-System"


# Set up the ESP in AP mode
setup_ap()
 
