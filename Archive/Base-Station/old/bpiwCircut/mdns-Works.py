import wifi
from mdns import Server

wifi.radio.hostname = 'bpi4'
print(wifi.radio.hostname)


allScannedSSID = []
scan = wifi.radio.start_scanning_networks()
print(scan)
for x in scan:
    allScannedSSID.append(x.ssid)
    
print(allScannedSSID)
import asyncio

async def setWi():   
    md = Server(wifi.radio)
    md.hostname = 'aa'

    wifi.radio.connect('Tell My Wi-Fi Love Her', 'GodIsGood!')
    print(md.hostname)

asyncio.run(setWi())

# neds to be Async
