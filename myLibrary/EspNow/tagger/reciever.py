"""
Receiver v1.5
 - esp now Recieves and prints
 - VIB works
 - 

npDone.py
"""
from machine import Pin
import espnow
import time, asyncio
from npDone import setNeo, red, green, blue, white, off
import network

setNeo(white)
time.sleep(1)

#{"tagger":"wakeup"}
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()                # Disconnect from last connected WiFi SSID

e = espnow.ESPNow()                  # Enable ESP-NOW
e.active(True)
e = espnow.ESPNow()                  # Enable ESP-NOW
e.active(True)

vib = Pin(44, Pin.OUT, Pin.PULL_DOWN)

def writeFile(data:str)-> None:
    """
    Write data to a file with time and pipe separator
    """
    print(data)
    setNeo(red)
    with open('logBase.txt', 'a+') as file:
        file.write(f'{time.time()} || {data} \n')
    #await asyncio.
   # sleep(.3)
    
async def espnow_rx():
    writeFile('espnow-rx-start')
    tNow = time.time()
    while True:
        setNeo(blue)
        host, msg = e.recv(5)
        if msg:
            #print('ln 50')
            setNeo(green) # green/
            vib.on()
            #print('(tx_pkts, tx_responses, tx_failures, rx_packets, rx_dropped_packets)')
            #(0, 0, 0, 12, 0)
            #[rssi, time_ms] #{b"H'\xe2\r\x80h": [-87, 1695109]} :     b'walk-1:37'
            data = time.time() - tNow, e.peers_table,": ",   msg
            writeFile(data)
            
            await asyncio.sleep(2) #keeps buzzing till last packet is recieved.
           # time.sleep(2)
            vib.off()
            writeFile('vib.off')
        #asyncio.run(espnow_tx(host, msg))
           # asyncio.run(espnow_tx(host, str(msg).split('|')[1]))
            #with open('logReciever.txt', 'a+') as file:
               # file.write(f'{data} \n')
            #print(msg)

async def keepAlive():
    while True:
        print('keepAlivesleep')

        await asyncio.sleep(500)
        print('sleep')
        
async def main():
    from time import sleep
    #sleep(4)
    asyncio.create_task(espnow_rx())
    
    asyncio.run(keepAlive()) #type: ignore


asyncio.run(main())


