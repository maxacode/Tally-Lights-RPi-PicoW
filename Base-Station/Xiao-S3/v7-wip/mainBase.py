"""
base-Station - Main:
v6.5

This is the main script for the base station API. It is responsible for handling the API requests and sending updates to the clients.
Functions and classes:
    
    - recvSetup: API endpoint to add a new client to the list of connected clients.
    - shutdown: API endpoint to shutdown the server.
    - app: Microdot application object to handle API requests.
    - setupWLAN: Function to setup the WLAN connection or AP mode based on the configuration.
    - setupIRQ: Function to setup the GPIO interrupts for reading the button state.
    - getGPIOState: Function to read the GPIO state when an interrupt is triggered.
    - scfdcendGPIOUpdate: Function to send the GPIO state to all connected clients.
    - mainThreads: Main function to start the API server and the main threads.
    - setupMappings: Function to setup the GPIO mappings based on the configuration.
    
    

 TODO:  Disable WLAN Before enalbe since soft reset doesnt clear it
Set WIFI to known state on startup: MicroPython does not reset the wifi peripheral after a soft reset. This can lead to unexpected behaviour. To guarantee the wifi is reset to a known state after a soft reset make sure you deactivate the STA_IF and AP_IF before setting them to the desired state at startup, eg.:
TODO: led # blicks when recvSetup is hit with tally


6.5 - 12/09
- new np class usage
-  


- 6.3
 - send to clinet retires 5 times
 - a lot of printFF changed to printF
 
 
-v6.2 - 12/05
- testing threads on sending packets to tallys - Works but multiple threads start and if 2 sends go to 1 tally then each will try to so total is alot more since thread 2 for try 2 keeps trying event though thread 1 knows device is offline




-v6.1 12/3
- removed pst setting and checking from getGPIOState since we do not need to check button value since buttons are used and no bounces accur with MCU or video Board
- sendtoclinet only retires 4 times instaed of 6 now
- added support for inital client connect to get new state

import network, timef

def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
  sta = network.WLAN(network.STA_IF); sta.active(False)
  ap = network.WLAN(network.AP_IF); ap.active(False)
  sta.active(True)
  while not sta.active():
      time.sleep(0.1)
  sta.disconnect()   # For ESP8266
  while sta.isconnected():
      time.sleep(0.1)
  return sta, ap

sta, ap = wifi_reset()


 - # TODO: kA not resetting after post is made
 

 
#TODO. boot.py file to run mainBase.py like in recivers setup
 
 """

import _thread

from gc import collect, mem_free # type: ignore

import network, asyncio # type: ignore
from json import loads
from requests import post # type: ignore
from machine import Pin, freq # type: ignore
#from time import time

from espNeoPixelClass import setNeo, red, green, blue, white, off, purple
setNeo(red, pid= 0, reset = False)
setNeo(green, pid = 1, reset = False)
setNeo(blue, pid = 2, reset = False)
setNeo(white, pid= 3, reset = False)
setNeo(purple, pid = 4, reset = False)



#def:
#BPI Micro
#Freq
freq(240000000) #ValueError: frequency must be 20MHz, 40MHz, 80000000, 160000000 or 240000000 32 didnt work
print(freq())
## External Files:
from lib.microdot.microdot import Microdot, Response,send_file, redirect
from lib.cors import CORS
from lib.utemplate import Template
from lib.connectToWlan import mainFunc
#from lib.npDone import setNeo, red, green, blue, white, off

from lib.utemplate2 import compiled
from lib.getConfig import getConf
from lib.printF import printF, printFF, printW

from time import sleep 
#Time since epoch in seconds
#timeNow: int  = time() #type: ignore 
# timeNow = 123214


# timeout durationg for request.post - 1 was to short, error'd out during long durating of lseep, 5 works so far
# TODO  find perfect duration amount
reqTimeOut: int = 3


gpioInMap: dict[str , list[int]] = {}  # {tally1, [15,16]}
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}

def setupMappings(config: object) -> None:
    """
    Function to setup the GPIO mappings and IRQ based on the config file
    params:
        config (object): The config object
    returns:
        None 
    """
    global gpioInMap
    tallyEnabled = (list({key: config.items('tallyEnabled')[key] for key in config.items('tallyEnabled') if key != 'title'}.values())) # type: ignore
     #['true', 'true', 'true', 'true']

    config.remove_option('gpioInput','title') # type: ignore
    for x in range(1,5):
        gpioInMap['tally'+str(x)] = loads(config.get('gpioInput', ('tally'+str(x)))) # type: ignore


    for x in gpioInMap.values(): #type: ignore
      # Find and output the key if the target number is found in any of the lists
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
        gpioIN = Pin(int(x[0]), Pin.IN, Pin.PULL_UP) #type: ignore
        gpioIN.on()
        gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
            # Second Pin
        gpioIN = Pin(int(x[1]), Pin.IN, Pin.PULL_UP) #type: ignore
        gpioIN.on()
        gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
    
    config.set('gpioInput', 'title', '!!pins that are from video switcher') # type: ignore
    printF(' Interrupts Setup: Done! ')   
 
####### API ######################
app: object = Microdot()
CORS(app, allowed_origins='*', allow_credentials=True)

clients: dict[str, str] = {} # clients example: {'192.168.88.1': '1'}

wlan = network.WLAN()
 
def getGPIOState(pin: object, *args:str ) -> None:
    """
    Function to read the GPIO state when an interrupt is triggered.
    Sends the GPIO state to all connected clients sendTo1Client function.
    params:
        pin (object): The pin object that triggered the interrupt.
        *args: str of TallyID ex: tally1
    returns:
        None
    """
        # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    #print(f'getGPIO State {pin=}, {args=}')
   
    
    if args:
        tallyID = args[0]
        pinNum = gpioInMap[tallyID][0]
        #await asyncio.sleep(.3)
    else:
        pinNum: int = int(str(pin)[4:-1])
        
        #Disable IRQ - Since pausing it makes it miss fast changes. Tested this. Without disable IRQ registers all chanes with Enalbed it misses half since it has to make post requests. might be idfferent if esp now
        
    #Pin(pinNum, Pin.IN, Pin.PULL_UP).irq(handler=None)

        # pause the handler
    setNeo(white, 120)
# extracts Just PIN num from pin object
    #gpioIN = Pin(int(pinNum), Pin.IN, Pin.PULL_UP
    tallyID = ''
        # Output the matching keys    for key,values in gpioInMap.items():
    curVal = ''
        # 
    for key,values in gpioInMap.items(): # key is tallyID full Str values is list of 2 pin mappings
        if pinNum in values:
            oldPinValue = 0
            pinValue = str(Pin(values[0]).value())+ str(Pin(values[1]).value())
            if oldPinValue == pinValue:
                tallyID = key  
                break
            else:
            #printFF(f'IntP: {pinNum} {key} {pinValue}')
                oldPinValue == pinValue
                await asyncio.sleep(.2)
                tallyID = key  
                curVal += str(pinValue)
              #  break 
    
                    # If clients exists then send color
                for ip, tallyIDInt in clients.items(): #key2 is IP val2 is TallyID just Int
                    if tallyIDInt in tallyID:
                        #printF('s3: ', ip[-3:0], curVal)
                       # asyncio.run(sendTo1Client(curVal, ip, tallyID))
                        printFF(f'IntP: {pinNum} {key} {pinValue}')

                        printF('  thread start', tallyID)
                        _thread.start_new_thread(sendTo1Client, (curVal, ip, tallyID))       
                    setNeo(blue, 120)
         
    # Enabling IRQ based on Pin param
   # Pin(pinNum, Pin.IN, Pin.PULL_UP).irq(handler=getGPIOState)
   
tCounter = 0 
def sendTo1Client(curVal: str, ip: str, tallyIDStr: str) -> None: #pinValue, ip,endPoint, tallyID):
        """
        Function to send the GPIO state to a single connected client.
        Params:
            curVal (str): The GPIO state to send ex: '01' or '10'.
            ip (str): The IP address of the client. ex: '192.168.88.1'
            tallyIDStr (str): The tally ID of the client. 'tally1'
            
        Returns:
            none
        """
       # printF('SendTo1Client Started: ', curVal, ip, tallyIDStr)
            #sendTo1Client(pinValue, ip, endPoint)
        tryCounter = 0
        global tCounter
        tallyIDInt = int((tallyIDStr[-1]))

        while True:
            try:
                tryCounter += 1
                tCounter += 1
                printF(f'    {tallyIDStr} | Sending  {tryCounter=} | {tCounter=}')
                url = f"http://{ip}:8080" + config.items('api')['ledControlEndpoint'] #type: ignore
                headers = {'led':str(curVal)}
                response = post(url,headers=headers,timeout = reqTimeOut)
                status = response.status_code #status: 200 | response: green off
                rText = response.text
                printF(f'        {tallyIDStr} s: {status} | r: {rText} | {tCounter=}')
                
                # Setting status Neos to correct status from response (R,G,B)
                if "red on" in rText:
                    setNeo(red, pid = tallyIDInt)
                elif "green on" in rText:
                    setNeo(green, pid = tallyIDInt)
                elif "blue on" in rText:
                    setNeo(blue, pid = tallyIDInt)
                    
                    
                if status != 200:
                    sleep(.2)
                    if tryCounter > 3:
                        printFF(f"           {tallyIDStr} is not avaialable, removing from clients")
                        try:
                            del clients[ip]
                        except:
                            pass
                        setNeo(off, 0, tallyIDInt)
                        break
                    

                if status == 200:
                    break
                
                #sleep(.4)
                
            except Exception as e:
                printW(f'           {tallyIDStr} timeout {e=}')
                #await asyncio.sleep(.1)
                sleep(.2)
                if tryCounter > 3:
                    printFF(f"     {tallyIDStr} ooo, removing ", tallyIDStr[-1])
                    try:
                        del clients[ip]
                    except:
                        pass 
                    printF(setNeo(off, pid = tallyIDInt))
                    break
                
        _thread.exit() 
        

@app.post('/recvSetup') #type: ignore
async def create_client(request):
    """
    API endpoint to add a new client to the list of connected clients.
    If Client already connnected, send back Dupe Request,
    If new client, add to clients Dict and send brightness levelsd
    params:
        request (object): The request object passed via Microdot
    returns:
        response (object): The response object. 'recvS:OK' or 'recvS:dupe' based on the client addition status.
        """
   # global timeNow
   # 3print(((time()) - timeNow) / 60)
   # timeNow = time()

    #Todo: if new client connects but different tally its still gets recvDupe but needs to be updated
    incomingIP = request.headers['ip']
    tallyIDJustInt: str = request.headers['tallyID']

    printFF('hit on /', request.method, request.client_addr, tallyIDJustInt)

    if incomingIP not in clients or clients[incomingIP] != tallyIDJustInt:
        printFF("#############  New Tally: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'])
        clients[incomingIP] = tallyIDJustInt
        printFF(f'{clients=}')
        tallyIDFullString: str = "tally"+tallyIDJustInt
        bright = int(config.items('tallyLEDStatus')[tallyIDFullString])  #type: ignore
        setNeo(blue, bright, int(request.headers['tallyID']))     
                
        printF('await setbrightness')

        asyncio.create_task(setBrightness(tallyIDFullString.split()))
        asyncio.create_task(sendCurrentGpio(tallyIDFullString))

        try:
            printF('returnign recvSetup')
            return 'recvS:OK', 200, {'Content-Type': 'text/html'}

        except Exception as Error:
            printFF(f'ln 253 {Error}')
 
#             #await asyncio.sleep(.5)


    
    else:
        printFF("#############  Updated Tally: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'])
        clients[incomingIP] = tallyIDJustInt
        printFF(f'{clients=}')
        tallyIDFullString: str = "tally"+tallyIDJustInt
        
        #getGPIOState(0, tallyIDFullString)

        printF('dupe recvSetup')
        asyncio.create_task(sendCurrentGpio(tallyIDFullString))
        
        try:
            printF('returnign recvSetup')
            return 'recvS:dupe', 208, {'Content-Type': 'text/html'}

        except Exception as Error:
            printFF(f'ln 283 {Error}')
 
 
    
async def keepAlive():
    while True:
        printF(f'kA time: {time.time()}')
        await asyncio.sleep(30)

async def sendCurrentGpio(tallyID: str):
    await asyncio.sleep(.2)
    printF('sending gpioState')
    getGPIOState(0, tallyID)

async def setBrightness(keys: set[str]):
    """
    Function to send the brightness values to the connected clients.
    params:
        keys (list): The list of tally IDs to send the brightness values.
    returns:
        None
    """
    tryCounter = 0
    # sleeping so create_client has time to send response back 
    await asyncio.sleep(.5)

    global clients
    for tallyToUpdate in keys:
        for key, value in clients.items():
            if value in tallyToUpdate:
                #printFF(f'{tallyToUpdate=} send brightness')

                red: str = config.items('tallyBrightness')[tallyToUpdate].split(',')[0] #type: ignore
                green: str = config.items('tallyBrightness')[tallyToUpdate].split(',')[1] #type: ignore
                blue:str = config.items('tallyBrightness')[tallyToUpdate].split(',')[2] #type: ignore
                while True:
                    try:
                        tryCounter += 1
                        # sending Post to IP and endpoint URL from config file with the red, green, blue values
                        url:str = f"http://{key}:8080" + config.items('api')['setTallyBrightness']  # type: ignore
                        headers: dict[str, str] = {'red':red, 'green':green, 'blue':blue}
                        response = post(url,headers=headers,timeout = reqTimeOut)
                        
                        status: int = response.status_code #status: 200 | response: green off
                        printF(f's1: {status} | r: {response.text}')
                        
                        if status != 200:
                            await asyncio.sleep(.2)
                            if tryCounter > 5:
                                printF('set brigh failed, break')
                                break
                        if status == 200:
                            break

                    except Exception as e:
                        await asyncio.sleep(.2)
                        if tryCounter > 5:
                            printF('set brigh failed, break')
                            break
                        
#TODO: a general func to send request.posts to and error handle instead of multiples timesasync def sendRequest(url: str, headers: dict):
    
async def updateWifi() -> None:
    """
    Function to send the WiFi credentials to all connected clients.
    params:
        None
    returns:
        None
    """
    url: str = f"http://{ip}:8080"+ config.items('api')['updatewifi']  # type: ignore

    headers = {'SSID':config.items('global')['wlanSSID'], 'PASS':config.items('global')['wlanPassword']} # type: ignore
    
    for ip in clients:
        printF('updateWifi Started: ', ip)
            #sendTo1Client(pinValue, ip, endPoint)
        tryCounter: int = 0 
        while True:
            try:
                tryCounter += 1
                printF(f'Sending to and try: ', ip, tryCounter)

                    #TODO Finish
                response = post(url,headers=headers,timeout = reqTimeOut)
                status = response.status_code #status: 200 | response: green off
                printF(f's2: {status} | r: {response.text}') 
                if status != 200:
                    await asyncio.sleep(.2)
                    if tryCounter > 5:
                        break
                if status == 200:
                    break
                
            except Exception as e:
                printW(f'           timeout {ip}',e)
                await asyncio.sleep(.4)
                tryCounter +=1

           
@app.route('/clients', methods=['GET', 'POST']) #type: ignore
async def clientsOnline(request):
    """
    Function to return the list of connected clients.
    params:
        request (object): The request object passed via Microdot
    returns:
        response (object): The response object. clientsOnline.html template rendered with the list of connected clients.
    """
    global clients
    printF('hit on /', request.method, request.client_addr)
    if request.method == 'POST':
        pass
    if request.method == 'GET':
        # Getting site so return whos online
        return await Template('clientsOnline.html').render_async(clients=clients)#, updated = False)
 
@app.route('/', methods=['GET', 'POST'])#type: ignore
async def index(request): 
    """
    Function to handle the index page requests, Read the config file and update the config based on the form data.
    params:
        request (object): The request object passed via Microdot
    returns:
        response (object): The response object. index2.html template rendered with the configuration.
    """
    global config
    printF('hit on /', request.method, request.client_addr)
    hitIP = request.client_addr
     # enable this to not compline html on th efly but once and done
    #Template.initialize(loader_class=compiled.Loader)
    brightChange = False
    keys = []
    if request.method == 'POST':
        # Chekcing if POST is to send Wifi to tallys
        if 'Send-Wifi' in request.headers:
            if request.headers['Send-Wifi'] == 'True':
                # Access any Config change
                printF('wifi update requested')
                asyncio.create_task(updateWifi())
            
        else:
            formData = loads(request.body.decode('utf-8'))
            for section in config.sections():
                for key in config.options(section):
                    form_key = f"{section}_{key}"  # Composite key for each field in the form
                    if form_key in formData:
                        #Checking if field is diff from saved field, if is pass if diff update config
                        if config.items(section)[key] == formData[form_key]: #type: ignore
                            pass
                        else:
                            printF(f'form key DIFF {config.items(section)[key]} {formData[form_key]} ') # type: ignore
                            #'form key DIFF 100, 200, 100 80, 81, 82 ',)
                            
                            # checking if specifically this key is changed if so it runs a specific fucntion.
                            if 'tallyBrightness' in section:
                                brightChange = True
                                keys.append(key)
                            
                            config.set(section, key, formData[form_key])
            
        config.write('baseConfig.json')
         
        if brightChange == True:
            printF("brightChange = True",keys)
            asyncio.create_task(setBrightness(keys))
        return await Template('index2.html').render_async(name=config)#, updated = True)
    
    
    elif request.method == 'GET':
         
        return await Template('index2.html').render_async(name=config)#, updated = False)



Response.default_content_type = 'text/html'

async def mainThreads()-> None:
    """
    Main function to start the API server and the main threads.
    params:
        None
    returns:
        None
    """
    #asyncio.create_task(keepAlive())
    setNeo(blue, 80, 0, True)
    asyncio.run(app.run(debug=True)) #type: ignore


# Main program execution
#def main():

config = getConf('baseConfig.json')
apMode, myIP = mainFunc(config,True)
printFF('myIP/ApMode: ', myIP, apMode)
setupMappings(config)
asyncio.run(mainThreads())


