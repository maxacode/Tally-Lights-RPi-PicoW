"""
This example script queries a local address and google. The google request is
delegated to be resolved as getaddrinfo call of socket.socket, the local address
utilizes mdns.
"""

import network
import uasyncio

from mdns_client import Client

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Tell My Wi-Fi Love Her", "GodIsGood!")
while not wlan.isconnected():
    import time

    time.sleep(1.0)

own_ip_address = wlan.ifconfig()[0]
print(own_ip_address)

loop = uasyncio.get_event_loop()
client = Client(own_ip_address)


async def query_mdns_and_dns_address():
    try:
        print(await client.getaddrinfo("google.de", 80))
    except OSError:
        print("DNS address not found")
    try:
        print(await client.getaddrinfo("tally3.local", 80))
    except OSError:
        print("MDNS address not found")


loop.run_until_complete(query_mdns_and_dns_address())