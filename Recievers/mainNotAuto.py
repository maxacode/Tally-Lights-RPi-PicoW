# Recievers Main Function
"""
v1.2
Reads the dip switches and sends a post request to the base station with the IP and Tally ID
Takes PST and PGM values from the POST request and sets the LED colors accordingly
Functions and classes:
    getDipSwitch() - Reads the dip switches and sets the tallyID
    ledPWM(pin, freq, duty) - Sets the PWM for the LED
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
import connectToWlan

from microdot import Microdot, send_file
app = Microdot()
from mdns_client import Client


with open('recvConfig.json','r') as f:
    config = json.load(f)
    #print(config)
    print(config["global"]["version"])

serverIP = ''
myIP = ''
serverMdnsName = config["global"]["baseStationName"]



client = Client('192.168.88.231')

async def query_mdns_and_dns_address():
    global serverIP
    while True:
        try:
            serverIP1 = (list(await client.getaddrinfo("tally.local", 8080)))
            serverIP = "http://"+serverIP1[0][4][0] + ":" + str(serverIP1[0][4][1])
            print("MDNS address found: ", serverIP)
            break
        except Exception as e:
            print("MDNS address not found: ", e)
            await asyncio.sleep(2)
 

def setupWLAN():
    global myIP, serverMdnsName
    print('apMode: ',config["global"]["apMode"])
    if config["global"]["apMode"] == True:
        print("Connecting to AP: ", config["global"]["apSSID"])
        myIP = connectToWlan.connectWLAN(config["global"]["apSSID"], config["global"]["apPassword"])

    elif config["global"]["apMode"] == False:
        print("Connecting to AP: ", config["global"]["wlanSSID"])

        myIP = connectToWlan.connectWLAN(config["global"]["wlanSSID"], config["global"]["wlanPassword"])
   
    
    print(f'######## Connected:  {serverMdnsName} myIP {myIP} ############')


    

tallyID = None
##### Reading 2 Dip Switches ####
def getDipSwitch():
    global tallyID
    # 00 = 1, 10 = 2, 01 = 3, 11 = 4
    # Dip switch 1
    dip1 = Pin(13, Pin.IN, Pin.PULL_UP)
    # Dip switch 2
    dip2 = Pin(14, Pin.IN, Pin.PULL_UP)
    # create 4 variables to store the values of the dip switches
    dp1 = dip1.value()
    dp2 = dip2.value()
    tallyID = None
    if dp1 == 0:
        if dp2 == 0:
            tallyID = 4
        else:
            tallyID = 3
    else:
        if dp2 == 1:
            tallyID = 1
        else:
            tallyID = 2
    print(f"Tally ID: {tallyID}")

getDipSwitch()
import time


lastTime = time.time()
 
async def keepAlive():
    # tracking last comm time
    currentTime = time.time()
    global lastTime
    if currentTime - lastTime > 10:
        print('No communication for 10 seconds')
        lastTime = currentTime
        await recvSetup()

# function to handle PIN PWM for LED
def ledPWM(pin, freq, duty):
    global output
    print('Pin: ', pin, 'Freq: ', freq, 'Duty: ', duty)
    pinLed = Pin(pin)
    pinLedPWM = PWM(pinLed)
    pinLedPWM.freq(freq)
    pinLedPWM.duty_ns(duty)
    #print("returning pin freq duty")
    return f"({pin}, {freq}, {duty})"

@app.route('/')
async def hello(request):
    response = send_file('index.html')
    return response
    #return html, 200, {'Content-Type': 'text/html'}

@app.post('/led')
async def led(request):
    lastTime = time.time()
    # turn on led 16 half brightness
    ledStatus = request.headers['ledStatus']
    print(f"ledStatus: {ledStatus}")
    red = 18
    green = 17
    blue = 16
    out = 'ack: '
    multiplier = 45000
    
    result = [list(ledStatus[i:i+2]) for i in range(0, len(ledStatus), 2)]
 
    try:
        ledPWM(blue, 500, 0)
        PST = int(result[tallyID-1][0])
        PGM = int(result[tallyID-1][1])
        if PST == 0 and PGM == 0:
            out = ledPWM(blue, 500, multiplier)
            
        print(f'PST/PGM: {PST} : {PGM}')
        out = out + ledPWM(red, 500, PGM*multiplier)
        out = out + ledPWM(green, 500, PST*multiplier)
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
    url = serverIP + config['api']['receiverSetup']
   # print(f'Url: {url}')
   # print(f'my ip: {myIP}')
    blue = 16

    lastTime = time.time()
    
    headers = {'ip':myIP, 'tallyID':str(tallyID)}
    
    while True:
        try:

            ledPWM(blue, 500, 20000)
            print('sending post: ', url, headers)

            response = requests.post(url,headers=headers,timeout=10)
            print('post sent')
            if response.status_code == 200:
                print('Request successful')
                print(response.text)
                ledPWM(blue, 500, 0)
                break
            else:
                print('Request failed')
                ledPWM(blue, 500, 0)
                await asyncio.sleep(3)
                
            # else:
            #     print('Request failed')
            #     print(response.text)
            #     ledPWM(blue, 500, 0)
            #     task = asyncio.create_task(recvSetup())
            #     await asyncio.sleep(10)
            #     ledPWM(blue, 500, 15000)
        except Exception as e:
            print(f"Error 201: {e}")
            ledPWM(blue, 500, 0)
            #task = asyncio.create_task(recvSetup())
            await asyncio.sleep(5)
            #ledPWM(blue, 500, 15000)
            #await recvSetup()
            
    
def sendPost(pin):
   # buttonSendRecvSetup.irq(handler=None)
    print('Button pressed', pin)
    recvSetup()
  #  buttonSendRecvSetup.irq(handler=sendPost)

 

async def mainThreads():
   # print(1.11)

    #task2 = asyncio.create_task(app.run(debug=True)())
    buttonSendRecvSetup = Pin(19, Pin.IN, Pin.PULL_DOWN)
    buttonSendRecvSetup.irq(trigger=Pin.IRQ_RISING, handler=sendPost)
    asyncio.create_task(keepAlive())
    
    task = asyncio.create_task(recvSetup())


    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":
    setupWLAN()
    asyncio.run(query_mdns_and_dns_address())

    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    print("xyz")
 
