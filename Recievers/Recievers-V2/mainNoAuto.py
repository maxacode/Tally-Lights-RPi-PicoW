# Recievers Main Function
"""
v1.6
Reads the dip switches and sends a post request to the base station with the IP and Tally ID
Takes PST and PGM values from the POST request and sets the LED colors accordingly
Functions and classes:
    getDipSwitch() - Reads the dip switches and sets the tallyID
    setNeo(color, level) - Sets the color and brightness
    hello(request) - Returns the index.html file
    led(request) - Sets the LED colors
    shutdown(request) - Shuts down the server
    recvSetup() - Sends a POST request to the base station with the IP and Tally ID
    mainThreads() - Main function that runs the server and the recvSetup function
    
"""

from machine import Pin, PWM
from time import sleep
import asyncio
import requests
import json
from connectToWlan import mainFunc
from npDone import setNeo

from microdot import Microdot, send_file
app = Microdot()
from mdns_client import Client


from getConfig import getConf

configFileName = 'recvConfig.json'

config = getConf(configFileName)


green = (255, 0, 0)
orange = (100, 200, 0)
yellow = (255, 230, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
violet = (0, 255, 100)

    
async def query_mdns_and_dns_address(myIP):
    global serverIP
    client = Client(myIP)
    while True:
        try:
            #print(config.items('global')['baseStationName'])
            serverIP1 = (list(await client.getaddrinfo(config.items('global')['baseStationName'], 8080)))
           # serverIP1 = (list(await client.getaddrinfo("tally2", 8080)))
            serverIP = "http://"+serverIP1[0][4][0] + ":" + str(serverIP1[0][4][1])
            print("!!!!! MDNS address found: ", serverIP)
            break
        except Exception as e:
            print("MDNS address not found: ", e)
            await asyncio.sleep(2)
     

##### Reading 2 Dip Switches ####
tallyID = 1

def getDipSwitch():
    global tallyID
    # 00 = 1, 10 = 2, 01 = 3, 11 = 4 
    # Dip switch 1
    dip1 = Pin(int(config.items('dipSwitch')['dip1']), Pin.IN, Pin.PULL_UP)
    # Dip switch 2
    dip2 = Pin(int(config.items('dipSwitch')['dip1']), Pin.IN, Pin.PULL_UP)
    # create 4 variables to store the values of the dip switches
    if dip1.value() == 0:
        if dip2.value() == 0:
            tallyID = 4
        else:
            tallyID = 3
    else:
        if dip2.value() == 1:
            tallyID = 1
        else:
            tallyID = 2       
    print(f"Tally ID: {tallyID}")
 
async def keepAlive():
    # tracking last comm time
  #  currentTime = time.time()
    global lastTime
    if currentTime - lastTime > 10:
        print('No communication for 10 seconds')
        lastTime = currentTime
        await recvSetup()

@app.route('/')
async def hello(request):
    response = send_file('index.html')
    return response
    #return html, 200, {'Content-Type': 'text/html'}

@app.post('/led')
async def led(request):

    ledStatus = request.headers['ledStatus']
    print(f"ledStatus: {ledStatus}")
    out = 'ack: '
  #  multiplier = 45000
    
    result = [list(ledStatus[i:i+2]) for i in range(0, len(ledStatus), 2)]
 
    try:
        setNeo(blue, 0)
        PST = int(result[tallyID-1][0])
        PGM = int(result[tallyID-1][1])
        if PST == 0 and PGM == 0:
            out = setNeo(blue, 50)
            
        print(f'PST/PGM: {PST} : {PGM}')
        out = out + setNeo(red, 500, config.items('tallyBrightness')('red'))
        out = out + setNeo(green, 500, config.items('tallyBrightness')('green'))
        E = out
        status = 200
        return out, status, {'Content-Type': 'text/html'}
    except Exception as E:
        print(f'Line 91: {E}')
        status = 418
        return E, status, {'Content-Type': 'text/html'}
         
@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

async def recvSetup():
    # Sending a post to base and recvSetup with IP and Tally ID
    url = serverIP + config.items('api')['receiverSetup']

    headers = {'ip':myIP, 'tallyID':str(tallyID)}
    
    while True:
        try:

            setNeo(blue,100)
            print('sending post: ', url, headers)

            response = requests.post(url,headers=headers,timeout=10)
            print('post sent')
            if response.status_code == 200:
                print('Request successful')
                print(response.text)
                setNeo(blue, 0)
                break
            else:
                print('Request failed')
                setNeo(blue, 0)
                await asyncio.sleep(3)

        except Exception as e:
            print(f"Error 201: {e}")
            setNeo(blue, 0)
            await asyncio.sleep(5)

    
def sendPost(pin):
   # buttonSendRecvSetup.irq(handler=None)
    print('Button pressed', pin)
    asyncio.run(recvSetup())
  #  buttonSendRecvSetup.irq(handler=sendPost)

 

async def mainThreads():
   # print(1.11)

    #task2 = asyncio.create_task(app.run(debug=True)())
    buttonSendRecvSetup = Pin(19, Pin.IN, Pin.PULL_DOWN)
    buttonSendRecvSetup.irq(trigger=Pin.IRQ_RISING, handler=sendPost)
   # asyncio.create_task(keepAlive())
    
    task = asyncio.create_task(recvSetup())


    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":
    # get Dip switch value
    getDipSwitch()

    myIP = mainFunc()

    asyncio.run(query_mdns_and_dns_address(myIP))

    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    print("xyz")
 
