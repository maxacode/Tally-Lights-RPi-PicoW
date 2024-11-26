#BASE v2 works

import espnow
import ubinascii
import network
import time, asyncio

#wlan_mac = wlan_sta.config('mac')
print(ubinascii.hexlify('\x80\x03\x84A6\xe8'))
# this: 4827e20d8068
sta = network.WLAN(network.STA_IF)    # Enable station mode for ESP

wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(False)

#sta.config(pm=sta.PM_NONE)
#sta.config(protocol=network.MODE_11B)  # Enables 802.11b mode

wlan_sta.active(True)
sta.disconnect()        # Disconnect from last connected WiFi SSID
e = espnow.ESPNow()     # Enable ESP-NOW
e.active(True)

"""
other esp:
Source address: Espressif_9d:84:af (a4:e5:7c:9d:84:af)
eth.src == a4:cf:12:cb:7e:1b


mine: eth.src == 48:27:e2:0d:80:68 or eth.src == 48:27:e2:0d:83:54

"""
 
from machine import freq
freq(240000000)

#peer1 = b'\x48\x27\xe2\x0d\x83\x54'   # MAC address of peer1's wifi interface
#peer1 = b'\xbb\xbb\xbb\xbb\xbb\xbb' #Bnote sure: roadcast
peer1 = b'\xff\xff\xff\xff\xff\xff' #broadcast
#try:
e.add_peer(peer1)                     # add peer1 (receiver1)
#except Exception as Error:
 #   print(f'{Error=}')
    
import random,machine
from neopixel import NeoPixel
import time 
pin_48 = machine.Pin(48)
np = NeoPixel(pin_48, 1,bpp=3, timing=1)
np[0] = (20,20,20) # yellow/green
np.write()



async def espTX():
    print('start espTX')
    tNow = time.time()
    print(f'1{tNow=}')

    counter = 0
    sleep = 5
    while True:
        await asyncio.sleep(sleep)
        np[0] = (0,150,0) # yellow/green
        np.write()
        counter += 1
        time_elapsed = (time.time()-tNow)
        sec = time_elapsed % 60
        min = (time_elapsed // 60) % 60
        HR = time_elapsed // 3600

        timeElap = (f"{HR=} {min=}, {sec=}")

        data = (f"SEND: {sleep=} | {counter=} | {timeElap=}")
        print(data)
        e.send(peer1, data, True)     # send commands to pear 1
        writeFile(data)
        #sleep ;= random.randint(0, 10)

        #[rssi, time_ms]
        #print(e.peers_table)
def writeFile(data):
    np[0] = (0,0,30) # yellow/green
    np.write()
    with open('logSender.txt', 'a+') as file:
        file.write(f'{time.time()} || {data} \n')
        
        
async def espRX():
    print('Start espRX')
    while True:
        host, msg = e.recv(0)
        if msg:
            np[0] = (30,0,0) # yellow/green
            np.write()
            data = (f" Received: {msg.decode()}")
            print(data)
            writeFile(data)

        await asyncio.sleep(0.2)  # Avoid blocking loop

        
async def keepAlive():
    while True:
        await asyncio.sleep(10)
        print('sleep')
        
async def main():
        
    
    task_tx = asyncio.create_task(espTX())
    task_rx = asyncio.create_task(espRX())
    
    await asyncio.gather(task_tx, task_rx)  # Run both tasks concurrently

   # while True:
   #     await asyncio.sleep(3)
    #asyncio.run(keepAlive())

writeFile("\n\n NEW INTSTANCE \n")

asyncio.run(main())

