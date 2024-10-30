# import urequests

# url = "http://192.168.88.234:8080/recvSetup"
# url = "http://tally.local:8080/recvSetup"

# data = {'ip':'192.168.88.247', 'tallyID':str(4)}


# response = urequests.post(url,headers=data)
# if response.status_code == 200:
#     print("POST request successful")
#     print(response.text)    
# else:
#     print("POST request failed with status code:", response.status_code)


"""
 
This example shows a one time discovery of available google cast services in the network.
This is probably the most efficient way to discover services, as it doesn't store any additional
local state after the query is done and should be used if memory is an issue in your application.
 
import uasyncio 

from mdns_client import Client
from mdns_client.service_discovery.txt_discovery import TXTServiceDiscovery

 
own_ip_address = '192.168.88.231'

loop = uasyncio.get_event_loop()
client = Client(own_ip_address)
discovery = TXTServiceDiscovery(client)


async def discover_once():
    print(await discovery.query_once("_googlecast", "_tcp", timeout=1.0))


loop.run_until_complete(discover_once())


This example script queries a local address and google. The google request is
delegated to be resolved as getaddrinfo call of socket.socket, the local address
utilizes mdns.
"""

import network
import asyncio

from mdns_client import Client
 

own_ip_address = '192.168.88.231'


#loop = uasyncio.get_event_loop()
client = Client(own_ip_address)


async def query_mdns_and_dns_address():
    try:
        serverIP1 = (list(await client.getaddrinfo("tally.local", 8080)))
        serverIP = serverIP1[0][4][0] + ":" + str(serverIP1[0][4][1])

        print("MDNS address found: ", serverIP)

    except Exception as e:
        print("MDNS address not found: ", e)


asyncio.run(query_mdns_and_dns_address())