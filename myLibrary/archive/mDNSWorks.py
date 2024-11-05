"""This example implements the service responder. Allowing to publish services with TXT record information
for the own local ip. For this, it requires a host name (if none is given an
micropython-{6 hexadecimal digits}) is generated. To randomize the name you can utilize
responder.generate_random_postfix().

 

"""

import network
import uasyncio

from mdns_client import Client
from mdns_client.responder import Responder


wlanSSID =  "Tell My Wi-Fi Love Her"
wlanPassword = "GodIsGood!"

wlan = network.WLAN(network.STA_IF)
wlan.config(hostname="mypicow")

wlan.active(True)
wlan.connect(wlanSSID, wlanPassword)
while not wlan.isconnected():
    import time

    time.sleep(1.0)

own_ip_address = wlan.ifconfig()[0]
print('own_ip: ', own_ip_address)

loop = uasyncio.get_event_loop()
client = Client(own_ip_address)
responder = Responder(
    client,
    own_ip=lambda: own_ip_address,
    host=lambda: "hellopico",
)


def announce_service():
    responder.advertise("tallyBase-Conf", "_tcp", port=8080, data={"tallySetup": "/recvSetup"})
    #responder.advertise()

    # If you want to set a dedicated service host name
   


def mainStuff():
   # setupWLAN():
    announce_service()
    loop.run_forever() # only to keep live, not needed with web server rnning - last thing

    
mainStuff()

