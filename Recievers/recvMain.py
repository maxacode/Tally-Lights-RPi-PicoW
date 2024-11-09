# Recievers Main Function
"""
v4.1 thonny
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
# from machine import WDT

# watchDog = WDT(timeout=60000)
# watchDog.feed()


# changing clock feq normal = 125000000
#machine.freq(62500000)

from gc import collect
from json import loads
from time import sleep
import asyncio
from requests import post
from connectToWlan import mainFunc
from lib.neopixel.npDone import setNeo

from lib.microdot.microdot import Microdot, Response
from cors import CORS
from utemplate import Template
from utemplate2 import compiled


app = Microdot()
from lib.mdns_client import Client

from printF import printF, printFF, printW


green = (255, 0, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
off = (0,0,0)
setNeo(blue, 100, 0, True)

def getConfig():
    from lib.getConfig import getConf

    configFileName = 'recvConfig.json'
    
    config = getConf(configFileName)

    collect()
    return config

# Function to start query of MDNS 
async def query_mdns_and_dns_address(myIP):
    global serverIP
    client = Client(myIP)
    retry = 0
    printFF(('    Getting MDNS for: ', config.items('global')['baseStationName']))

    while True:
        printF(('retry mds: ', retry))
        
        if retry >= 8:
            printF("retry more than 8")
            retry = 0
            break
        try:
            retry += 1
            
            serverIP1 = (list(await client.getaddrinfo(config.items('global')['baseStationName'], config.items('api')['port'])))
           # serverIP1 = (list(await client.getaddrinfo("tally2", 8080)))
            serverIP = "http://"+serverIP1[0][4][0] + ":" + config.items('api')['port']
            printFF(("           !!!! MDNS address found: ", serverIP))

            config.items('global')['baseStationIP'] = str(serverIP1[0][4][0])
            config.write('recvConfig.json')
            break
        except Exception as e:
            retry += 1
            printFF(("        MDNS address not found: ",e))
            await asyncio.sleep(1)
            
    printF("starting recvSetu ln 75")
    await recvSetup(config)



##### Reading 2 Dip Switches ####

def getDipSwitch():
    global tallyID
    # 00 = 1, 10 = 2, 01 = 3, 11 = 4 
    # Dip switch 1
    dip1 = Pin(int(config.items('dipSwitch')['dip1']), Pin.IN, Pin.PULL_UP)
    # Dip switch 2
    dip2 = Pin(int(config.items('dipSwitch')['dip2']), Pin.IN, Pin.PULL_UP)
    # create 4 variables to store the values of the dip switches
#     from time import sleep
#     while True:
#         sleep(1)
#         printF(dip1.value(), dip2.value())
#         
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

@app.route('/', methods=['GET', 'POST'])
async def index(request):
    global config
    printF('hit on /', request.method)
     # enable this to not compline html on th efly but once and done
    #Template.initialize(loader_class=compiled.Loader)

    if request.method == 'POST':
        formData = loads(request.body.decode('utf-8'))
        for section in config.sections():
            for key in config.options(section):
                form_key = f"{section}_{key}"  # Composite key for each field in the form
                if form_key in formData:
                    #Checking if field is diff from saved field, if is pass if diff update config
                    if config.items(section)[key] == formData[form_key]:
                        pass
                    else:
                        printF(f'form key DIFF {config.items(section)[key]} {formData[form_key]} ')
                        config.set(section, key, formData[form_key])
            
        config.write('recvConfig.json')
        return await Template('index2.html').render_async(name=config)
        #return await Template('index.html').render_async(name=config)
    
    
    elif request.method == 'GET':
        collect()
        return await Template('index2.html').render_async(name=config)



Response.default_content_type = 'text/html'
@app.post('/setBrightness')
async def setBrightness(request):
    printW(request.url, request.headers)
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
    printF('led ln 150 start')
    printF(request.url, request.client_addr, request.headers['led']) #('/led', None, {'ledStatus': '00000100', 'Host': '192.168.88.229', 'Connection': 'close'})
    setNeo(blue, 200)
    #ledStatus = request.headers['ledStatus']
    #printW(f"ledStatus: {ledStatus}")
    out = 'Code Error recv main 164: '
  #  multiplier = 45000
    headAll = request.headers
    if "led" in headAll:
        head = request.headers['led']
        if "0" == head[0]:
            setNeo(red,int(config.items('tallyBrightness')['red']))
            out = 'red on'
        if "1" == head[0]:
            out = 'red off'
            #setNeo(blue, 80, 0)
        if "0" == head[1]:
            if "0" == head[0]:
                setNeo(red,int(config.items('tallyBrightness')['red']))
                out = 'red on'
            else:
                setNeo(green,int(config.items('tallyBrightness')['green']))
                out = 'green on'          
        if "1" == head[0]:
            out = 'green off'
    else:
        setNeo(blue, 80, 0)
        out = 'FAILED'
        
    return out, 200, {'Content-Type': 'text/html'}


@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

async def recvSetup(config):
    # Sending a post to base and recvSetup with IP and Tally ID
    printF(f"ln 163 {serverIP}{config.items('api')['receiverSetup']}")
    url = f"{serverIP}{config.items('api')['receiverSetup']}"

    headers = {'ip':myIP, 'tallyID':str(tallyID)}
    retry = 0    
    while True:
        printF('ln 169 while True')
        # We are trying to get MDNS IP if server does not reply after 5 attemps
        retry += 1
        if retry >= 4:
            #printF('retry more that 5')
            retry = 0
            await query_mdns_and_dns_address(myIP)
            break
        try:
            printFF(('sending post: ', url, headers))
            setNeo(blue,100)
            response = post(url,headers=headers,timeout=2)
            printF('post sent')
            if response.status_code == 200:
                printFF('Request successful', response.text)
                setNeo(blue, 100, 0, True)
                break
            else:
                printF('Request failed')
                setNeo(red, 100,0, True)
                await asyncio.sleep(1)
                

        except Exception as e:
            printFF(f"Error recvSetup ln 201: {e}")
            setNeo(red,100, 0, True)
            await asyncio.sleep(2)


async def mainThreads():
    printF('ln 207 mainThread start')

   # asyncio.create_task(keepAlive())


    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":

    
    config = getConfig() #GC Done
       # get Dip switch value
    getDipSwitch()
    myIP = mainFunc(config,True) # GC Done
    printFF(myIP)
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
        
    asyncio.create_task(recvSetup(config))

    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    printF("xyz")
 
