"""
Base v1.2

 - setup espNow stuff
 - main - all tasks with asncio

npDone.py
"""
import time, asyncio
from machine import Pin, deepsleep, lightsleep, DEEPSLEEP, SLEEP,reset_cause
from time import sleep
import network, espnow
from json import dumps
import esp32

from npDone import setNeo, red, green, blue, white, off

setNeo(blue)

dsEnabled = True

def writeFile(*args, **kwargs )-> None:
    """
    Write data to a file with time and pipe separator
    """
    setNeo(red)
    curTime = time.time()
    print(curTime, args, kwargs)

    with open('logBase.txt', 'a+') as file:
        file.write(f'{curTime=} || {args} {kwargs} \n')
    #await asyncio.
   # sleep(.3)
    
def espTX()-> None:
    """
    Send commands to peer broadcast
    """
    global kA, e
    kA = 0 #reset keepAlive counter to 0
    writeFile('start espTX')
    setNeo(green)
    data = dumps({"tagger":"wakeup"})
    e.send(peer1, str(data), True)     # send commands to pear 1
   # await asyncio.
    sleep(.3)

    writeFile('end espTX')
    setNeo(blue)
    
def keepAlive()-> None:

    """    
    Sleep and increase counter by X and if button is pressed reset it. 
    After Y time, do deep sleep
    
   1 machine.PWRON_RESET
   2 machine.HARD_RESET
   3 machine.WDT_RESET
   4 machine.DEEPSLEEP_RESET
   5 machine.SOFT_RESET
   
    """
    kA = 0
    while True:
        if kA >= 5:
            writeFile(f'Going to ds: {kA=}')
            setNeo((20,20,20))
            sleep(1)
            if dsEnabled:
                writeFile('ln 62')
                setNeo(off)
                sleep(1)
                #deepsleep() # deepsleep()
                #writeFile('ln 75 reset_cause:', reset_cause())
                kA = 0
                #writeFile(f'wake from ls {kA=}')
            else:
                sleep(10)
                kA = 0
        else:
            kA += 1
            setNeo((20,0,30))
            #await asyncio.
            # Try light sleep or deepsleep
            writeFile(f'awaiting sleep: {kA=}')
            espTX()
            sleep(.3)
            setNeo(blue)
            
async def main()-> None:
    """
    Main Loop to handle everything
    Params: None
    Returns: None
    """
   # writeFile('IRQ Setup')
    #butt1 = Pin(44, Pin.IN, Pin.PULL_UP)  # pin 43
    #butt1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=espTX)
    asyncio.run(keepAlive())

tNow = time.time()
writeFile(' ---------------------------- ')
writeFile(f"\n\n NEW INTSTANCE | {tNow=}\n")
writeFile('ln 104 reset_cause:', reset_cause())

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

butt1 = Pin(12, Pin.IN)#, Pin.PULL_DOWN)  # pin 43
#butt1.off()
#esp32.wake_on_ulp(False)
#esp32.gpio_deep_sleep_hold(False)
esp32.wake_on_ext0(pin = butt1, level = esp32.WAKEUP_ANY_HIGH)
#esp32.wake_on_ext0(pin = butt1, level = esp32.WAKEUP_ALL_LOW)

keepAlive()
 

