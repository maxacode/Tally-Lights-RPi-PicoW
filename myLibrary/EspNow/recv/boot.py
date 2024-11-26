#RECV- v1 backup

import network
import espnow,time, asyncio


from machine import Pin
from neopixel import NeoPixel
import time 
pin_48 = Pin(48)
np = NeoPixel(pin_48, 1,bpp=3, timing=1)
np[0] = (20,20,20) # yellow/green
np.write()

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()                # Disconnect from last connected WiFi SSID

e = espnow.ESPNow()                  # Enable ESP-NOW
e.active(True)
    
peer1 = b'\xff\xff\xff\xff\xff\xff' #broadcast
e.add_peer(peer1)                     # add peer1 (receiver1)

#e.add_peer(peer1)                     # add peer1 (receiver1)


async def espnow_tx(host: str, counter):
    await asyncio.sleep(.1)
    e.send(peer1, f'recv0k: {counter}', True)     # send commands to pear 1
    np[0] = (25,0,0) # red
    np.write()
    print('e sent')
    #np[0] = (0,0,0) # green/
    #np.write()
    
async def espnow_rx():
    print('espnow-rx-start')
    tNow = time.time()
    while True:
        np[0] = (0,0,0) # green/
        np.write()
       # print('while true')
        host, msg = e.recv()
        np[0] = (0,30,0) # green/
        np.write()
        #print('(tx_pkts, tx_responses, tx_failures, rx_packets, rx_dropped_packets)')
        #(0, 0, 0, 12, 0)
        #[rssi, time_ms] #{b"H'\xe2\r\x80h": [-87, 1695109]} :     b'walk-1:37'
        data = e.peers_table,": ",   msg
        print(data)
        asyncio.run(espnow_tx(host, str(msg).split('|')[1]))
                    
        with open('logReciever.txt', 'a+') as file:
            file.write(f'{data} \n')
        #print(msg)
        np[0] = (0,0,0) # green/
        np.write()

async def keepAlive():
    while True:
        await asyncio.sleep(10)
        print('sleep')
        
async def main():
    asyncio.create_task(espnow_rx())
    
    asyncio.run(keepAlive()) #type: ignore


asyncio.run(main())




