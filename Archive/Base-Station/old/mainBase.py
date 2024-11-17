"""
base-Station - Main: v3.4 - Thonny

This is the main script for the base station API. It is responsible for handling the API requests and sending updates to the clients.
Functions and classes:
    
    - recvSetup: API endpoint to add a new client to the list of connected clients.
    - shutdown: API endpoint to shutdown the server.
    - app: Microdot application object to handle API requests.
    - setupWLAN: Function to setup the WLAN connection or AP mode based on the configuration.
    - setupIRQ: Function to setup the GPIO interrupts for reading the button state.
    - getGPIOState: Function to read the GPIO state when an interrupt is triggered.
    - sendGPIOUpdate: Function to send the GPIO state to all connected clients.
    - mainThreads: Main function to start the API server and the main threads.
    - setupMappings: Function to setup the GPIO mappings based on the configuration.
    

 """
from gc import collect, mem_free
gc1 =  mem_free()

import network, asyncio
from json import loads
from requests import post
from machine import Pin, freq
from printF import printF, printFF, printW
#def:
#125000000 W0rks
#225000000 # works
#255000000 # half th etime works 
#270000000 # SLower and Wifi Scan no return
freq(225000000)

## External Files:
from lib.microdot.microdot import Microdot, Response
from cors import CORS
from utemplate import Template
from mdns_client import Client
from mdns_client.responder import Responder
from connectToWlan import mainFunc
from lib.neopixel.npDone import setNeo
from utemplate2 import compiled

gc2 = mem_free()
print(gc1 - gc2)

"""
131120

123056 # just mdns folder

122416  neoPixel

98800  Microdot


93936 utempllte 2

89376 
"""
print(mem_free())

# 48464 , 48512 no sys, 48480 os.listdir only, 48544 no os.listdir, 48656 no if in getConfig
# 48736 No json import , 48624 only import post, 48720 no send-file
# no mdns 94416

green = (255, 0, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
off = (0,0,0)
white = (255,255,255)
def getConfig():
    from lib.getConfig import getConf

    configFileName = 'baseConfig.json'
    
    config = getConf(configFileName)
    #printF(config, config.sections())

    collect()
    return config


gpioInMap = {}
def setupMappings(config):
    global gpioInMap
    current_button_map = [] 
    tallyEnabled = (list({key: config.items('tallyEnabled')[key] for key in config.items('tallyEnabled') if key != 'title'}.values())) #['true', 'true', 'true', 'true']

    config.remove_option('gpioInput','title')
    for x in range(1,5):
        gpioInMap['tally'+str(x)] = loads(config.get('gpioInput', ('tally'+str(x))))
        
      # Find and output the key if the target number is found in any of the lists
    
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    for x in gpioInMap.values():
        printF(x)
        gpioIN = Pin(int(x[0]), Pin.IN, Pin.PULL_UP)
        gpioIN.on()
        gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
            # Second Pin
        gpioIN = Pin(int(x[1]), Pin.IN, Pin.PULL_UP)
        gpioIN.on()
        gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
    
    config.set('gpioInput', 'title', '!!pins that are from video switcher')
    #config.write('baseConfig.json')
# 	  y = 1
#     for x in tallyEnabled:
#         if x:
#             gpioInDict = config.items('gpioInput')['tally'+str(y)]
#             splitGpioIn = gpioInDict.split(',')#22 <class 'int'>
#           #  current_button_map.append(gpioInput['tally'+str(y)])
#              #Setting IRQ for pins that are enalbed - this worked when hooked up to board
#             gpioIN = Pin(int(gpioInMap[0]), Pin.IN, Pin.PULL_UP)
#             gpioIN.on()
#             gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
#                 # Second Pin
#             gpioIN = Pin(int(splitGpioIn[1]), Pin.IN, Pin.PULL_UP)
#             gpioIN.on()
#             gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
#         
#         elif x == False:
#             current_button_map.append([0,0])
#         y += 1
    #current map [[16, 17], [18, 19], [20, 21], [22, 26]]
    
    #del current_button_map, tallyEnabled, gpioInput#, gpioIN
    #collect()
 
def announce_service(myIP):
    # Client is a mdns object 
    client = Client(myIP)
    printF(config.items('global')['baseStationName'])
    
    responder = Responder(
        client,
        own_ip=lambda: myIP,
        host=lambda: config.items('global')['baseStationName'])
    collect()
    return responder


def responder(responder):
    responder.advertise("tallyAdver8080", "_hello._tcp", port=8080, data={"tallySetup": "/recvSetup"})
    collect()



 
####### API ######################
app = Microdot()
CORS(app, allowed_origins='*', allow_credentials=True)

clients = {}
current_button_state = []  # Initialize global variable for button state

curButMap = []


 
 
def getGPIOState(pin):
    printF(' new getGPIOState 156')
    setNeo(white, 120)
   # global curGpioState,gpioState, gpioIN, curButMap
    #gpioIN.irq(handler=None)
    pinNum = str(pin)[8:10]
    printF(pin)
    pinValue = pin.value()
    printF("Pin went high: ", pinNum, pinValue )
    gpioState = ''
    printF('*************** Clients: ', clients)
    tallyID = ''
    printF(clients)
    # Output the matching keys    for key,values in gpioInMap.items():
    for key,values in gpioInMap.items():
             
        if int(pinNum) == values[0]:
            endPoint = '/PGM'
            tallyID  = key


        elif int(pinNum) == values[1]:
            endPoint = '/PST'
            tallyID  = key
            
    for key2, val2 in clients.items():
        if val2 in tallyID:
            ip =  key2
        
            printF('sending to: ', ip, endPoint, pinValue)
            asyncio.create_task(sendTo1Client(pinValue, ip, endPoint, tallyID))
            
              
    setNeo(blue, 120)
    collect()



current_button_state = ''



gpioState = ''

currentClientLEDPin = ''
def sendGPIOUpdate(state):
    global clients
    if state is not None:
        # Function to send POST requests to all connected clients
       # printF(f"  Sending to clients {clients} ")
        tryCounter = 0
        global currentClientLEDPin
        for ip in clients.keys():
            currentClientLEDPin = config.items("tallyLEDStatus")["tally"+clients[ip]].split(',')[0]
            collect()   
            asyncio.run(sendTo1Client(state, clients, ip, int(clients[ip])))
    collect()

async def setBrightness(red, green, blue, ip,):
            tryCounter = 0 
            while True:
                try:
                    collect()
                    tryCounter += 1
                    # sending Post to IP and endpoint URL from config file with the red, green, blue values
                    url = f"http://{ip}:8080" + config.items('api')['setTallyBrightness']  # Replace with your client's endpoint
                    headers = {'red':red, 'green':green, 'blue':blue}
                    response = post(url,headers=headers,timeout = 1)

                    if response.status_code != 200:
                        await asyncio.sleep(.3)
                        if tryCounter > 5:
                            collect()
                            break

                except Exception as e:
                    collect()
                    await asyncio.sleep(.3)
 
async def sendTo1Client(pinValue, ip,endPoint, tallyID):
        printFF('snedTo1Client Started: ', pinValue, ip, endPoint)
            #sendTo1Client(pinValue, ip, endPoint)
        tryCounter = 0 
        while True:
            try:
                collect()
                tryCounter += 1
                printF('Sending to and try: ', ip, tryCounter)
                url = f"http://{ip}:8080/led"  # Replace with your client's endpoint
                headers = {endPoint:str(pinValue)}
                response = post(url,headers=headers,timeout = 1)
                status = response.status_code #status: 200 | response: green off
                printFF(f'status: {status} | response: {response.text}') 
                if status != 200:
                    await asyncio.sleep(.5)
                    if tryCounter > 5:
                        printFF(f" Reg            {ip} is not avaialable, removing from clients",ip)
                        del clients[ip]
                        printF(tallyID)
                        printF(setNeo(off, 0, int(tallyID[-1])))
                        collect()
                        break
                if status == 200:
                    break
                
            except Exception as e:
                collect()
                printW(f'           ln 251 {e} ID: {ip}')
                await asyncio.sleep(.5)
                if tryCounter > 5:
                    printFF(f"E             {ip} is not avaialable, removing from clients",ip, tallyID[-1])
                    del clients[ip]
                    printF(setNeo(off, 0, int(tallyID[-1])))

                    collect()
                    break
           

####### baseAPI #################
# recvSetup
@app.post('/recvSetup')
async def create_client(request):
    collect()

    printFF("#############  New Tally: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'])
    
    clients[request.headers['ip']] = request.headers['tallyID'] 
    
    tallyID = "tally"+request.headers['tallyID']

    bright = int(config.items('tallyLEDStatus')[tallyID]) 
    setNeo(blue, bright, int(request.headers['tallyID']))     
    collect()
    return current_button_state, 200, {'Content-Type': 'text/html'}
 

      
@app.route('/', methods=['GET', 'POST'])
async def index(request):
    global config
    print('299: ', mem_free())
    collect()
    print('301: ', mem_free())

    #Template.initialize(loader_class=compiled.Loader)

    if request.method == 'POST':
        for section in config.sections():
            for key in config.options(section):
                form_key = f"{section}_{key}"  # Composite key for each field in the form
                collect()
                if form_key in request.form:
                    #Checking if field is diff from saved field, if is pass if diff update config
                    if config.items(section)[key] == request.form[form_key]:
                        pass
                    else:
                        config.set(section, key, request.form[form_key])
            
        collect()
        config.write('baseConfig.json')
        return await Template('index2.html').render_async(name=config)
        #return await Template('index.html').render_async(name=config)
    
    
    elif request.method == 'GET':
        collect()
        return await Template('index2.html').render_async(name=config)



Response.default_content_type = 'text/html'

async def mainThreads():
    setNeo(blue, 80, 0, True)
    asyncio.run(app.run(debug=True))



# Main program execution
if __name__ == "__main__":
    printFF("ln 366 staritng getConfig")
    
    config = getConfig() #GC Done
   # irq()
    
     #GC Done
   # collect()
    
    #seutp Wifi or AP mode
    myIP = mainFunc(config,True) # GC Done
    printFF('myIP: ', myIP)
    
    collect()
    #make hostname.local available
    responder(announce_service(myIP)) # GC Done
    collect()
    setupMappings(config)
    asyncio.run(mainThreads())
   # asyncio.run(app.run(debug=True))

