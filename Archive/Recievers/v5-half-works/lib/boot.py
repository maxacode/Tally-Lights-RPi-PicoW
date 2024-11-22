# Recievers Main Function
"""
v5.1 done 452 11/11
# adding single func for Ruquest Posts'
Functions and classes:
    getDipSwitch() - Reads the dip switches and sets the tallyID
    hello(/) - Returns the index.html file
    led(/led) - Sets the LED colors
    setBrightness(/setBrightness) - Sets the brightness of the LED red, green, blue
    shutdown(/shutdown) - Shuts down the server
    recvSetup post baseIP(/recvSetup) - Sends a POST request to the base station with the IP and Tally ID
    mainThreads() - Main function that runs the server and the recvSetup function
    keepAlive() - Sleeps for 10seconds then adds 10 to counter, if over 30 triggers recvSetup. kA is reset on every postMade
"""
#TODO all LED's brigtness msut be from config file not static

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
from requests import post,get
from connectToWlan import mainFunc
from lib.neopixel.npDone import setNeo, green, red, blue, off, white

from lib.microdot.microdot import Microdot, Response
from cors import CORS
from utemplate import Template
from utemplate2 import compiled


app = Microdot()
from lib.mdns_client import Client

from printF import printF, printFF, printW



setNeo(blue, 100, 0, True)

reqTimeOut = 2

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
            
            return serverIP
        except Exception as e:
            retry += 1
            printFF(("        MDNS address not found: ",e))
            await asyncio.sleep(1)
            
    #printF("starting recvSetu ln 75")
    #await asyncio.run_until_complete(recvSetup(config))



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
 

async def makePost(method: str, url:str, headers: dict[str, str or int])-> str:
        """
        Function to make a post from given Params
        Params:
            method: str, GET OR POST
            url (str): Full URL to send to
            Headers dict[str, str]:  ех: {'led':str(curVal), '234', 'on'}
            
        Returns:
            str: True if Success or False or Failed and MSG Error message
        
        """
        tryCounter = 0 

        printF(f'makePost Start try: {tryCounter}')
            #sendTo1Client(pinValue, ip, endPoint)
        while True:
            tryCounter += 1
            try:
                printF(f'makePost Start : {url} {headers}')

                if method == 'POST':
                    response = post(url,headers=headers,timeout = reqTimeOut)
                elif method == "GET":
                    response = get(url,headers=headers,timeout = reqTimeOut)
                    
                status = response.status_code #status: 200 | response: green off
                printFF(f's2: {status} | r: {response.text}') 
                if status != 200:
                    if tryCounter > 5:
                        #printFF(f" 			makePost Fails")
                        return  [False, 'makePost Fails']
                    await asyncio.sleep(.5)

                if status == 200:
                    return [True, 200]
                    
            except Exception as e:
                printW(f'           timeout {url}', e)
                await asyncio.sleep(.5)
                
                if tryCounter > 5:
                    return 'makePost Failes with E'
 
    
    
    
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



@app.post('/updatewifi')
async def updateWifi(request):
    global kA
    kA = 0
    printFF('hit on /updateWifi', request.method, request.headers)
    try:
        SSID = request.headers['SSID']
        PASS = request.headers['PASS']
        printW(f"SSID: {SSID}, PASS: {PASS}")
        
        config.items('global')['wlanSSID'] = SSID
        config.items('global')['wlanPassword'] = PASS
 
        config.write('recvConfig.json')
        printW("Updated Wifi")
        return 'Updated Wifi', 200, {'Content-Type': 'text/html'}
    
    except Exception as E:
        printF(f'Line 165: {E}')
        status = str(E) + " line 165 /set brightness"
        return status, 418, {'Content-Type': 'text/html'}
    
@app.post('/setBrightness')
async def setBrightness(request):
    global kA
    kA = 0
    printFF('hit on /setBrightness', request.method, request.client_addr)
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
    global kA
    kA = 0
    printFF('hit on /', request.method, request.client_addr)
    #printF(request.url, request.client_addr, request.headers['led']) #('/led', None, {'ledStatus': '00000100', 'Host': '192.168.88.229', 'Connection': 'close'})
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

async def recvSetup(config,serverIP,myIP):
    retry = 0 
    global kA
    kA = 0
    while True:

        # We are trying to get MDNS IP if server does not reply after 5 attemps
        retry += 1
        if retry >= 4:
            printF('starting query mdns ln 237')
            retry = 0
            #await query_mdns_and_dns_address(myIP)
            serverIP = await query_mdns_and_dns_address(myIP)
            printF('ln 238 serverIp: ', serverIP)
           # break
                    # Sending a post to base and recvSetup with IP and Tally ID
        printF(f"ln 163 {serverIP}{config.items('api')['receiverSetup']}")
        url = f"{serverIP}{config.items('api')['receiverSetup']}"
        headers = {'ip':myIP, 'tallyID':str(tallyID)}        
        status = await makePost('POST', url, headers)
        if status[0]:
            break
            
            
kA = 0
async def keepAlive():
    global kA
    printF(291, kA)
    while True:
        try:
            await asyncio.sleep(int(config.items('hidden')['heartbeat']))
            kA += int(config.items('hidden')['heartbeat'])
            
            printF(294, kA)
            
            if kA >= int(config.items('hidden')['keepAlivePush']):
                printF(297,kA)
                kA = 0
                asyncio.create_task(recvSetup(config,serverIP,myIP))
                
        except Exception as e:
            printFF(302, e)
            await asyncio.sleep(30)
            machine.reset()
            
        
async def mainThreads(apMode, myIP):
    printF('ln 207 mainThread start')
    global serverIP
    if apMode:
        pass
    elif apMode == False:
        # iF not AP mode try connect to server
        try:
            printF('228')
            # if IP is in config try to connect just in case its the same as last time
            if isinstance(config.items('global')['baseStationIP'], str):
                printF('ln 230')
                serverIP = "http://"+str(config.items('global')['baseStationIP']) + ":8080"
            else:
                printF(('ln 233: ', config.items('global')['baseStationIP']))
                await asyncio.run(query_mdns_and_dns_address(myIP))
        except Exception as e:
            printFF(235, e)
            await asyncio.run(query_mdns_and_dns_address(myIP))
            
        asyncio.create_task(recvSetup(config,serverIP,myIP))

        asyncio.create_task(keepAlive())
        
    asyncio.run(app.run(debug=True))



# Main program execution
if __name__ == "__main__":

    serverIP = ''
    config = getConfig() #GC Done
       # get Dip switch value
    getDipSwitch()
    apMode, myIP = mainFunc(config,True) # GC Done
    printFF(myIP, apMode)

    
    asyncio.run(mainThreads(apMode, myIP))
    # Main thread continues running while the other threads execute
  




