
"""
WLAN.isconnected()
In case of STA mode, returns True if connected to a WiFi access point and has a valid IP address. In AP mode returns True when a station is connected. Returns False otherwise.
"""
import network
import time
import socket

wifiSSID = "Tally-Lights"
wifiPass = "LSDkj%$#8ew7lka4"
hostName = "Tally-System"

def web_page():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body><h1>Hello World</h1></body></html>
         """
  return html

# if you do not see the network you may have to power cycle
# unplug your pico w for 10 seconds and plug it in again
def ap_mode(ssid, password):

    # Just making our internet connection
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=wifiSSID, password=wifiPass)
    ap.active(True)
    network.hostname(hostName)

    while ap.active() == False:
        pass
    return('AP Mode Is Active, You can Now Connect \n IP Address To Connect to:: ' + ap.ifconfig()[0])


 