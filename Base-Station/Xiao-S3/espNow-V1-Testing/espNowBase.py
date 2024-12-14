"""
v1.0 Base test ESP NOW
- ideas:
    - base polls each pin state every x seconds then broadcasts if state is different from last'
        - Does not keep track of tally Status just fire n forget.
        - test bare bone with all 4 tallys for speed/errors %
        - maybe if msg is acked then keep tally State
        
    - use IRQ and read then read again .2 then send update. 
    
"""

#Built in
import asyncio
from machine import Pin
import network, espnow
from json import dumps
import esp32
from time import sleep

#mine
from onBLed import lon, loff, tester
#test LEDS
#tester()

from SwriterClass import writeFile
writeFile  = writeFile("base.txt")
wf = writeFile.wf
wfp = writeFile.wfp


    
def espTX(data: dict[str:str|list])-> None:
    """
    Send commands to peer broadcast
    Params:
    - data: json data
    
    Returns:
    - none
    
    """
    wf(f'ESPNOW sending: {data}')
    dataJSON = dumps(data)
    e.send(peer1, str(dataJSON), True)     # send commands to peer 1

    
### Setup ESP Now
sta = network.WLAN(network.STA_IF)    # Enable station mode for ESP
wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(False)
wlan_sta.active(True)
sta.disconnect()        # Disconnect from last connected WiFi SSID
e = espnow.ESPNow()     # Enable ESP-NOW
e.active(True)
peer1 = b'\xff\xff\xff\xff\xff\xff' #broadcast
#peer1 = b"H'\xe2\r\x80h"
try:
    e.add_peer(peer1)
except:
    pass

t1r = Pin(1, Pin.IN, Pin.PULL_DOWN)
t1g = Pin(2, Pin.IN, Pin.PULL_DOWN)

t2r = Pin(3, Pin.IN, Pin.PULL_DOWN)
t2g = Pin(4, Pin.IN, Pin.PULL_DOWN)

t3r = Pin(5, Pin.IN, Pin.PULL_DOWN)
t3g = Pin(6, Pin.IN, Pin.PULL_DOWN)

t4r = Pin(43, Pin.IN, Pin.PULL_DOWN)
t4g = Pin(7, Pin.IN, Pin.PULL_DOWN)

oldPinValues = ''
def readPins():
    global oldPinValues
    t1Pins = f"{t1r.value()}{t1g.value()}{t2r.value()}{t2g.value()}{t3r.value()}{t3g.value()}{t4r.value()}{t4g.value()}"
    if oldPinValues == t1Pins:
        pass
    else:
        oldPinValues = t1Pins
        espTX({'tu':t1Pins})
    
    
while True:
    readPins()
    sleep(.01)