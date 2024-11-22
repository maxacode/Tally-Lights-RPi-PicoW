# Recievers Main Function
"""
v7.2

Functions and classes:
    getconfig() - reads the config file
    query_mdns - get mdns of tally .local hostname in config file
    getDipSwitch() - Reads the dip switches and sets the tallyID
    makePost - sends a http post with requests library and given url/headers. Returns Status (Add returning response)
    index(/) - home page with config that can be chagned
    updateWifi(/updatewifi) - Base sends new Wifi Configs
    setBrightness(/setBrightness) - Sets the brightness of the LED red, green, blue
    led(/led) - Sets the LED colors
    shutdown(/shutdown) - Shuts down the server
    recvSetup post baseIP(/recvSetup) - Sends a POST request to the base station with the IP and Tally ID
    keepAlive() - Sleeps for 10seconds then adds 10 to counter, if over 30 triggers recvSetup. kA is reset on every postMade
    mainThreads() - Main function that runs the server and the recvSetup function

v 7.2 10pm 11/20
ka disabled !!

Files changed:
    - printF
    - npTestClass in lib.neopixel
    - test.py - imporitng new npTestClass
    
Changes:
- clenaing up code
- added time tracker to printF
- static Brightness levels at start of program
    - Works but con is when config is updated it wont chagne until reboot
    - all but 1 setNeo updated since first setNeo is before config
- all GC/Collect removed
- removed timoeout global var and made is as a parm in makePost that has defualt 5 seconds (tested and workes so far but lower end)
     - reqTimeOut:int = 5 
    
v7.1 10pm 11/19
 - connectWlan, recvConf, boot.py
# Works: adding single func for Ruquest Posts'

#TODO lower clock freq but wifi still works
"""

from machine import Pin, reset
# from machine import WDT

# watchDog = WDT(timeout=60000)
# watchDog.feed()


# changing clock feq normal = 125000000
#machine.freq(62500000)

from json import loads
from time import sleep
import asyncio
from requests import post,get


# my lib
from connectToWlan import mainFunc
from lib.neopixel.npDone import setNeo, green, red, blue, off, white
from lib.microdot.microdot import Microdot, Response
from cors import CORS
from utemplate import Template
from utemplate2 import compiled
app = Microdot()
from lib.mdns_client import Client
from printF import printF, printFF, printW



def getConfig():
    from lib.getConfig import getConf

    configFileName = 'recvConfig.json'
    
    config = getConf(configFileName)

    return config

# Function to start query of MDNS 
async def query_mdns_and_dns_address(myIP):
    global serverIP
    client = Client(myIP)
    retry = 0
    printFF(f"    Getting MDNS for: {config.items('global')['baseStationName']}")

    while True:
        printF(f'retry mdns: {retry=}')
        
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
    return serverIP
      
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
 

async def makePost(method:str,  url:str,  headers:dict[str|iter, str|iter],  reqTimeOut:int = 5 ) -> list[bool, int]:
        """
        Function to make a request.post or get with Passed Method,Headers, Timeout
        
        Params:
            method: str, GET OR POST
            url (str): Full URL to send to
            Headers dict[str, str]:  ех: {'led':str(curVal), '234', 'on'}
            reqTimeOut: timeout whe making a request default 5 seconds ( tested and this seems sufficiuent but also on lower side)
            
        Returns:
            list[bool, str]: True if Success or False or Failed and MSG Error message
        
        """

        try:
            printF(f'makePost Start : {url} {headers}')

            if method == 'POST':
                #response = post(url,headers=headers)`
                response = post(url,headers=headers,timeout = reqTimeOut)
               # response = post(url,headers=headers)
# TODO: why timeout = reqTimeOut does not work? to short of a time? or wrong syntax?

            elif method == "GET":
                response = get(url,headers=headers,timeout = reqTimeOut)
                
            status = response.status_code #status: 200 | response: green off
            printFF(f'{status=} | {response.text=}') 
            if status != 200:
                return  [False, status]
            elif status >= 200 and status < 300:
                return [True, status]
        except Exception as e:
            printW(f'        ln 167 timeout {e=}')
            
            return [False, 400]



    
    
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
        return await Template('index2.html').render_async(name=config)



Response.default_content_type = 'text/html'



@app.post('/updatewifi')
async def updateWifi(request):
    global kA
    kA = 0
    printF('hit on /updateWifi', request.method, request.headers)
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
    printF('hit on /setBrightness', request.method, request.client_addr)
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
    printF(f'hit on /led {request.method=} , {request.client_addr=}, {request.headers["led"]=}')
    #printF(request.url, request.client_addr, request.headers['led']) #('/led', None, {'ledStatus': '00000100', 'Host': '192.168.88.229', 'Connection': 'close'})
    setNeo(blue, blueLevel)
    
    #ledStatus = request.headers['ledStatus']
    #printW(f"ledStatus: {ledStatus}")
    out = 'Code Error recv main 164: '
  #  multiplier = 45000
    headAll = request.headers
    if "led" in headAll:
        head = request.headers['led']
        # 0 in 0 index = first button in GPIO In pressed
        if "0" == head[0]:
            setNeo(red, redLevel)
            out = 'red on'
        if "1" == head[0]:
            out = 'red off, blue on'
            setNeo(blue, blueLevel, 0)
        if "0" == head[1] or "1" == head[1]:
            if "0" == head[0]:
                setNeo(red,redLevel)
                out = 'red on'
            elif "0" == head[1]:
                setNeo(green, greenLevel)
                out = 'green on'          
       # if "1" == head[0]:
          #  setNeo(blue, 80, 0)
         #   out = 'green off, blue on '
            
    else:
        setNeo(blue, blueLevel)
        out = 'FAILED'
    printFF(out)
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
        setNeo((255,165,0), whiteLevel)

        # We are trying to get MDNS IP if server does not reply after 5 attemps
        retry += 1
        printF(f'recvSetup {retry=}')
        if retry >= 3:
            printF('starting query mdns ln 237')
            retry = 0
            #await query_mdns_and_dns_address(myIP)
            serverIP = await query_mdns_and_dns_address(myIP)
            printFF(f'ln 238 {serverIP=} ')
           # break
                    # Sending a post to base and recvSetup with IP and Tally ID
        url = f"{serverIP}{config.items('api')['receiverSetup']}"
        headers = {'ip':myIP, 'tallyID':str(tallyID)}
      #  status = response.status_code
        status = await makePost('POST', url, headers)
        printFF(f'{status=}')
        if status[1] >= 200 and status[1] < 300:
       # if status == 200:
            setNeo(blue, blueLevel)
            break
        #elif status[0] == 208:
        else:
            setNeo(off, 0)
            await asyncio.sleep(1)
            #TODO: do something if status is not 200, like disable red/green light if resonse is recvS:dupe
            
kA = 0
async def keepAlive():
    global kA
    while True:
        try:
            await asyncio.sleep(int(config.items('hidden')['heartbeat']))
            kA += int(config.items('hidden')['heartbeat'])
                        
            if kA >= int(config.items('hidden')['keepAlivePush']):
                printF(f'{kA=}')
                kA = 0
                asyncio.create_task(recvSetup(config,serverIP,myIP))
                
        except Exception as e:
            printF(f'ln 320 {e=}')
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



config = getConfig()
redLevel = int(config.items('tallyBrightness')['red'])
blueLevel = int(config.items('tallyBrightness')['blue'])
greenLevel = int(config.items('tallyBrightness')['green'])
whiteLevel = int(config.items('tallyBrightness')['white'])


setNeo(blue, 50, 0, True)



serverIP = ''
   # get Dip switch value
getDipSwitch()
apMode, myIP = mainFunc(config,True) # GC Done
printFF(myIP, apMode)
asyncio.run(mainThreads(apMode, myIP))
# Main thread continues running while the other threads execute

if __name__ == "__main__":
    main()





