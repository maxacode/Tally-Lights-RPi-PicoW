"""
base-Station - Main: v2.4 - Thonny

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

import network, asyncio
from json import loads
from requests import post
from machine import Pin, freq
from printF import printF, printFF, printW
#def:
#BPI Micro
#Freq
freq(240000000)#ValueError: frequency must be 20MHz, 40MHz, 80000000, 160000000 or 240000000 32 didnt work

## External Files:
from lib.microdot.microdot import Microdot, Response,send_file, redirect
from cors import CORS
from utemplate import Template
from mdns_client import Client
from mdns_client.responder import Responder
from connectToWlan import mainFunc
from lib.npDone import setNeo, red, green, blue, white, off
from utemplate2 import compiled

"""
131120

123056 # just mdns folder

122416  neoPixel

98800  Microdot


93936 utempllte 2

89376 
"""

# 48464 , 48512 no sys, 48480 os.listdir only, 48544 no os.listdir, 48656 no if in getConfig
# 48736 No json import , 48624 only import post, 48720 no send-file
# no mdns 94416

def getConfig():
    from lib.getConfig import getConf

    configFileName = 'baseConfig.json'
    
    config = getConf(configFileName)

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


    for x in gpioInMap.values():
      # Find and output the key if the target number is found in any of the lists
    
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
        gpioIN = Pin(int(x[0]), Pin.IN, Pin.PULL_UP)
        gpioIN.on()
        gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
            # Second Pin
        gpioIN = Pin(int(x[1]), Pin.IN, Pin.PULL_UP)
        gpioIN.on()
        gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
    
    config.set('gpioInput', 'title', '!!pins that are from video switcher')
    printFF(' Interrupts Setup: Done! ') 



 
####### API ######################
app = Microdot()
CORS(app, allowed_origins='*', allow_credentials=True)

clients = {}
current_button_state = []  # Initialize global variable for button state

curButMap = []


from time import sleep
pSt = ''
#times = 0
def getGPIOState(pin):
    setNeo(white, 120)
    global pSt, times
    #global curGpioState,gpioState, gpioIN, curButMap
    #gpioIN.irq(handler=None)
    #sleep(.4)
    pinNum = str(pin)[4:-1]
    tallyID = ''
        # Output the matching keys    for key,values in gpioInMap.items():
    curVal = ''
    for key,values in gpioInMap.items():
        printF(key, values, values[0], values[1]) #tally1 [1, 2] 1 2
        if int(pinNum) in values:
            pinValue = Pin(values[0]).value() + Pin(values[1]).value()
            if pinValue == pSt:
                #print('same: ',times)
                #times += 1
                pass
            elif pinValue != pSt:
            #imes = 0
                pSt = pinValue
                printFF(f'IntP: {pinNum} v:', Pin(int(values[0])).value(), Pin(int(values[1])).value())
                gpioState = ''
                printF('*************** Clients: ', clients)
                tallyID  = key
                curVal += str(Pin(values[0]).value()) + str(Pin(values[1]).value())
                printF(tallyID, curVal)
                break
                
    for key2, val2 in clients.items():
        if val2 in tallyID:
            ip =  key2
            printF('s3: ', ip[-3:0], curVal)
            asyncio.run(sendTo1Client(curVal, ip, tallyID))
            
                  
        setNeo(blue, 120)
        collect()


    #gpioIN.irq(handler=getGPIO)




async def setBrightness(keys):
        tryCounter = 0
        #await asyncio.sleep(1)
        global clients
        for tallyToUpdate in keys:
            for key, value in clients.items():
                if value in tallyToUpdate:
                    printFF(f'{tallyToUpdate} send brightness')
                    red = config.items('tallyBrightness')[tallyToUpdate].split(',')[0]
                    green = config.items('tallyBrightness')[tallyToUpdate].split(',')[1]
                    blue = config.items('tallyBrightness')[tallyToUpdate].split(',')[2]

                    while True:
                        try:
                            tryCounter += 1
                            # sending Post to IP and endpoint URL from config file with the red, green, blue values
                            url = f"http://{key}:8080" + config.items('api')['setTallyBrightness']  # Replace with your client's endpoint
                            headers = {'red':red, 'green':green, 'blue':blue}
                            response = post(url,headers=headers,timeout = 1)
                            
                            status = response.status_code #status: 200 | response: green off
                            printFF(f's1: {status} | r: {response.text}')
                            
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

async def sendTo1Client(curVal, ip, tallyID): #pinValue, ip,endPoint, tallyID):
        printF('SendTo1Client Started: ', curVal, ip, tallyID)
            #sendTo1Client(pinValue, ip, endPoint)
        tryCounter = 0 
        while True:
            try:
                collect()
                tryCounter += 1
                printF('Sending to and try: ', ip, tryCounter)
                url = f"http://{ip}:8080/led"  # Replace with your client's endpoint
                headers = {'led':str(curVal)}
                response = post(url,headers=headers,timeout = 1)
                status = response.status_code #status: 200 | response: green off
                printFF(f's2: {status} | r: {response.text}') 
                if status != 200:
                    await asyncio.sleep(.5)
                    if tryCounter > 5:
                        printFF(f"           {ip} is not avaialable, removing from clients",ip)
                        del clients[ip]
                        printF(setNeo(off, 0, int(tallyID[-1])))
                        collect()
                        break
                if status == 200:
                    break
                
            except Exception as e:
                collect()
                printW(f'           timeout {ip}')
                await asyncio.sleep(.5)
                if tryCounter > 5:
                    printFF(f"E             {ip} ooo, removing ", tallyID[-1])
                    del clients[ip]
                    printF(setNeo(off, 0, int(tallyID[-1])))
                    break
           

####### baseAPI #################
# recvSetup
@app.post('/recvSetup')
async def create_client(request):
    collect()
    if request.headers['ip'] not in clients:
        printFF("#############  New Tally: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'])
        clients[request.headers['ip']] = request.headers['tallyID'] 
        tallyID = "tally"+request.headers['tallyID']
        bright = int(config.items('tallyLEDStatus')[tallyID]) 
        setNeo(blue, bright, int(request.headers['tallyID']))     
        asyncio.create_task(setBrightness(tallyID.split()))
        return 'recvS:OK', 200, {'Content-Type': 'text/html'}
    else:
        return 'recvS:dupe', 200, {'Content-Type': 'text/html'}

@app.route('/', methods=['GET', 'POST'])
async def index(request):
    global config
    printFF('hit on /', request.method, request.client_addr)
    hitIP = request.client_addr
     # enable this to not compline html on th efly but once and done
    #Template.initialize(loader_class=compiled.Loader)
    brightChange = False
    keys = []
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
                        printFF(f'form key DIFF {config.items(section)[key]} {formData[form_key]} ') #('form key DIFF 100, 200, 100 80, 81, 82 ',)
                    
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
        collect()
        return await Template('index2.html').render_async(name=config)#, updated = False)



Response.default_content_type = 'text/html'

async def mainThreads():
    setNeo(blue, 80, 0, True)
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__": 
    config = getConfig() #GC Done
    myIP = mainFunc(config,True) # GC Done
    printFF('myIP: ', myIP)
    setupMappings(config)
    asyncio.run(mainThreads())