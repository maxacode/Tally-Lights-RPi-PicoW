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
import socket
import time
from machine import Pin

led = Pin("LED", Pin.OUT)
led.value(1)



print("Starting WLAN Connection")

ssid = 'Tell My Wi-Fi Love Her'
password = 'GodIsGood!'

def flashLed(times,duration,msg):
    x = 0
    while x < times:
        time.sleep(duration)
        print(msg, " ", time.time())
        x += 1
        led.toggle()
        time.sleep(duration)

def connectWLAN():
    led = Pin("LED", Pin.OUT)
    led.value(1)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
 
    #wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        print(wlan.status())
        led.toggle()
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for WLAN Connection...')
        time.sleep(1)
        
        
        # Handle connection error
    if wlan.status() != 3:
        flashLed(9999, 0.05,'Failed to connect to WLAN')
        print('customRaise: network connection failed')

    else:
        print('Connected')
        status = wlan.ifconfig()
        print( f'ip = {str(status)}')
        
        flashLed(2, 0.25, 'Connected to WLAN')
        
    
    led.on()

#connectWLAN()
