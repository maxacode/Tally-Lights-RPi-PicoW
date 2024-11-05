# Recievers Main Function
"""
v2.1
# 
Functions and classes:
    getDipSwitch() - Reads the dip switches and sets the tallyID
    hello(/) - Returns the index.html file
    led(/led) - Sets the LED colors
    setBrightness(/setBrightness) - Sets the brightness of the LED red, green, blue
    shutdown(/shutdown) - Shuts down the server
    recvSetup post baseIP(/recvSetup) - Sends a POST request to the base station with the IP and Tally ID
    mainThreads() - Main function that runs the server and the recvSetup function
    
"""

from machine import Pin

# changing clock feq normal = 125000000
#machine.freq(62500000)



from time import sleep
import asyncio
import requests
import json
from connectToWlan import mainFunc
from npDone import setNeo

from microdot import Microdot, send_file
app = Microdot()
from mdns_client import Client


#from getConfig import getConf

#configFileName = 'recvConfig.json'

#config = getConf(configFileName)


green = (255, 0, 0)
orange = (100, 200, 0)
yellow = (255, 230, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
violet = (0, 255, 100)

serverIP = ''
printFOn = True # All Msg
printFFOn = True # only impt
printWOn = True

def printF(*args):
    print("                   ---------                       ")

    if printFOn == True:
        print(args)
            
def printFF(*msg):
    print("                   ---------                       ")
    if printFFOn == True:
        print(msg)
    elif printFOn == True:
        printF(msg)
def printW(*msg):
    print("                   ---------                       ")

    if printWOn == True:
        print(msg)
    elif printFon == True:
        printF(msg)

# Function to start query of MDNS 
async def query_mdns_and_dns_address(myIP):
    global serverIP
    printF('ln 61, query mdns started')
    client = Client(myIP)
    retry = 0
    while True:
        printF(('retry mds: ', retry))
        
        if retry >= 8:
            printF("retry more than 8")
            retry = 0
            break
        try:
            retry += 1
            
            printF(('    Getting MDNS for: ', config.items('global')['baseStationName']))
            serverIP1 = (list(await client.getaddrinfo(config.items('global')['baseStationName'], config.items('global')['port'])))
           # serverIP1 = (list(await client.getaddrinfo("tally2", 8080)))
            serverIP = "http://"+serverIP1[0][4][0] + ":" + config.items('global')['port']
            printF(("            !!!!!!!!!!!!!!!!!! MDNS address found: ", serverIP))

            config.items('global')['baseStationIP'] = str(serverIP1[0][4][0])
            config.write('recvConfig.json')
            break
        except Exception as e:
            retry += 1
            printF(("        MDNS address not found: ",e))
            await asyncio.sleep(1)
            
    printF("starting recvSetu ln 75")
    #await recvSetup()


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
    printFF(f"Tally ID: {tallyID}")
 
async def keepAlive():
    # tracking last comm time
  #  currentTime = time.time()
    global lastTime
    if currentTime - lastTime > 10:
        printF('No communication for 10 seconds')
        lastTime = currentTime
        await recvSetup()

@app.route('/')
async def hello(request):
    printW(request.url, request.json, request.headers)
    
    response = send_file('index.html')
    return response
    #return html, 200, {'Content-Type': 'text/html'}

@app.post('/setBrightness')
async def setBrightness(request):
    printW(request.url, request.json, request.headers)
    try:
        red = int(request.headers['red'])
        green = int(request.headers['green'])
        blue = int(request.headers['blue'])
        printW(f"red: {red}, green: {green}, blue: {blue}")
        config.items('tallyBrightness')['red'] = red
        config.items('tallyBrightness')['green'] = green
        config.items('tallyBrightness')['blue'] = blue

        config.write('recvConfig.json')

        return 'Brightness Set', 200, {'Content-Type': 'text/html'}
    
    except Exception as E:
        printF(f'Line 165: {E}')
        status = str(E) + " line 165 /set brightness"
        return status, 418, {'Content-Type': 'text/html'}
    
@app.post('/led')
async def led(request):
    printW(request.url, request.json, request.headers) #('/led', None, {'ledStatus': '00000100', 'Host': '192.168.88.229', 'Connection': 'close'})

    ledStatus = request.headers['ledStatus']
    printW(f"ledStatus: {ledStatus}")
    out = 'ack: '
  #  multiplier = 45000
    
    result = [list(ledStatus[i:i+2]) for i in range(0, len(ledStatus), 2)] #('ln 148 result', [['0', '0'], ['0', '0'], ['0', '1'], ['0', '0']])
    printW('ln 148 result', result)
    
    try:
        setNeo(blue, 0)
        PGM = int(result[tallyID-1][0]) # PGM live
        PST = int(result[tallyID-1][1]) # PST Preview
        printW(f'PST/PGM: {PST} : {PGM}')
        printW(config.items('tallyBrightness')['red'])
        print(type(config.items('tallyBrightness')['red']))
        
        if PST == 0 and PGM == 0:
            printW(f'159')

            out = out + '00' #+ str(setNeo(blue, 50))
            return out, 200, {'Content-Type': 'text/html'}
        if PGM == 1:
            printW(f'164')
            out = out + '1,0 red'

            setNeo(red, int(config.items('tallyBrightness')['red']))
        if PST == 1:
            printW(f'167')
            out = out +  '0,1,green '
            setNeo(green, int(config.items('tallyBrightness')['green']))
            
        if PST == 1 and PGM == 1:
            out = out + " 1,1 green/red"
            setNeo(red, int(config.items('tallyBrightness')['red'], green, int(config.items('tallyBrightness')['green'])))
            #etNeo(green, int(config.items('tallyBrightness')['green']))

        printW(out)
        return out, 200, {'Content-Type': 'text/html'}
    except Exception as E:
        printF(f'Line 172: {E}')
        status = 418
        return E, status, {'Content-Type': 'text/html'}
         
@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

async def recvSetup():
    # Sending a post to base and recvSetup with IP and Tally ID
    printF('ln 163 recvSetup started')
    url = serverIP + config.items('api')['receiverSetup']

    headers = {'ip':myIP, 'tallyID':str(tallyID)}
    retry = 0    
    while True:
        printF('ln 169 while True')
        # We are trying to get MDNS IP if server does not reply after 5 attemps
        retry += 1
        if retry >= 2:
            printF('retry more that 5')
            retry = 0
            await query_mdns_and_dns_address(myIP)
            break
        try:
            printF(('sending post: ', url, headers))
            setNeo(blue,100)
            response = requests.post(url,headers=headers,timeout=2)
            printF('post sent')
            if response.status_code == 200:
                printF('Request successful')
                printF(response.text)
                setNeo(blue, 0)
                break
            else:
                printF('Request failed')
                setNeo(blue, 0)
                await asyncio.sleep(1)

        except Exception as e:
            printFF(f"Error recvSetup ln 201: {e}")
            setNeo(blue, 0)
            await asyncio.sleep(2)


async def mainThreads():
    printF('ln 207 mainThread start')

   # asyncio.create_task(keepAlive())
    
    #task = asyncio.create_task(recvSetup())


    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":
    # get Dip switch value
    getDipSwitch()

    myIP,config = mainFunc()
    try:
        printF('228')
        if isinstance(config.items('global')['baseStationIP'], str):
            printF('ln 230')
            serverIP = "http://"+str(config.items('global')['baseStationIP']) + ":8080"
        else:
            printF(('ln 233: ', config.items('global')['baseStationIP']))
            asyncio.run(query_mdns_and_dns_address(myIP))
    except Exception as e:
        printF(235)
        printF(e)
        asyncio.run(query_mdns_and_dns_address(myIP))
        
    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    printF("xyz")
 
