"""
Base v1.2

 - setup espNow stuff
 - main - all tasks with asncio
- done

npDone.py
"""
import time, asyncio
from machine import Pin, deepsleep, lightsleep, DEEPSLEEP, SLEEP
from time import sleep
import network, espnow
from json import dumps
import esp32

from npDone import setNeo, red, green, blue, white, off

setNeo(blue)

def writeFile(data:str)-> None:
    """
    Write data to a file with time and pipe separator
    """
    print(data)
    #setNeo(red)
    with open('logBase.txt', 'a+') as file:
        file.write(f'{time.time()} || {data} \n')
    #await asyncio.
    #sleep(.)
    
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
    """
    kA = 0
    while True:
        if kA >= 7:
            writeFile(f'Going to ds: {kA=}')
            setNeo((20,20,20))
            sleep(1)
            deepsleep() # deepsleep()
        else:
            kA += 3
            setNeo((20,0,30))
            #await asyncio.
            # Try light sleep or deepsleep
            writeFile(f'awaiting sleep: {kA=}')
            espTX()
            sleep(1)
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
writeFile(f"\n\n NEW INTSTANCE | {tNow=}\n")

### Setup ESP Now
sta = network.WLAN(network.STA_IF)    # Enable station mode for ESP
wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(False)
wlan_sta.active(True)
sta.disconnect()        # Disconnect from last connected WiFi SSID
e = espnow.ESPNow()     # Enable ESP-NOW
e.active(True)
peer1 = b'\xff\xff\xff\xff\xff\xff' #broadcast
try:
    e.add_peer(peer1)
except:
    pass

butt1 = Pin(12, Pin.IN)#, Pin.PULL_DOWN)  # pin 43
esp32.wake_on_ext0(pin = butt1, level = esp32.WAKEUP_ANY_HIGH)

keepAlive()
#while True:
# setNeo(red)
# sleep(2)
#deepsleep()
# setNeo((20,0,30))
# sleep(1)
# blue 2s
# white .5
# purple .3
#  red file .2
#  green .5
# purple .3
# white sleep 1s
# #asyncio.run(main())

