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


import network, json, requests, asyncio, gc, os
from machine import Pin
from printF import printF, printFF, printW

## External Files:
from lib.microdot.microdot import Microdot, send_file, Response
from cors import CORS

from utemplate import Template

from mdns_client import Client
from mdns_client.responder import Responder
 
from connectToWlan import mainFunc

from lib.neopixel.npDone import setNeo


def getConfig():
    from lib.getConfig import getConf
    curDir = str(os.listdir())
    if "recvConfig" in curDir:
        baseStation = False
        configFileName = 'recvConfig.json'
    elif "baseConfig" in curDir:
        baseStation = True
        configFileName = 'baseConfig.json'
    
    config = getConf(configFileName)
    #print(config, config.sections())
    gc.collect()
    del getConf
    return config, baseStation



def setupMappings(config):
    current_button_map = [] 
    tallyEnabled = (list({key: config.items('tallyEnabled')[key] for key in config.items('tallyEnabled') if key != 'title'}.values()))
    printF(tallyEnabled)
    gpioInput = config.items('gpioInput')
   # gpioInput.pop('title')
    y = 1

    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    y = 1
    for x in tallyEnabled:
        if x:
            current_button_map.append(gpioInput['tally'+str(y)])
             #Setting IRQ for pins that are enalbed
            gpioIN = Pin(int(gpioInput['tally'+str(y)].split(',')[0]), Pin.OUT, Pin.PULL_UP)
            gpioIN.on()
            gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
                # Second Pin
            gpioIN = Pin(int(gpioInput['tally'+str(y)].split(',')[1]), Pin.OUT, Pin.PULL_UP)
            gpioIN.on()
            gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
        
        elif x == False:
            current_button_map.append([0,0])
        y += 1
    #current map [[16, 17], [18, 19], [20, 21], [22, 26]]
    
    del current_button_map, tallyEnabled, gpioInput, gpioIN
    
    gc.collect()


 

def announce_service(myIP):
    # Client is a mdns object 
    client = Client(myIP)
    printF(config.items('global')['baseStationName'])
    
    responder = Responder(
        client,
        own_ip=lambda: myIP,
        host=lambda: config.items('global')['baseStationName'])
    gc.collect()
    return responder


def responder(responder):
    responder.advertise("tallyAdver8080", "_hello._tcp", port=8080, data={"tallySetup": "/recvSetup"})
    gc.collect()



 
####### API ######################
app = Microdot()
CORS(app, allowed_origins='*', allow_credentials=True)

clients = {}
current_button_state = []  # Initialize global variable for button state

curButMap = []
def setupIRQ():
    # Create Interupts based on if Tally is Enabled in config and with the pins in config
    global gpioIN,curButMap
    tallyEnabled = (list({key: config.items('tallyEnabled')[key] for key in config.items('tallyEnabled') if key != 'title'}.values())) # ['true', 'true', 'true', 'true'])
    gpioInput = config.items('gpioInput')
    printF('tallyEnabled ln 123', tallyEnabled) #{'tally3': '20,21', 'tally2': '18,19', 'tally4': '22,26', 'tally1': '16,17'})

    
    y = 1
    for x in tallyEnabled:
        if x:
            curButMap.append(gpioInput['tally'+str(y)])
        elif x == False:
            curButMap.append([0,0])
        y += 1
    printF('cur but map: ', curButMap) # cur but map:  ['17, 16', '19, 18', '21, 20', '26, 22']

    for x in curButMap:
        for y in x.split(','):
           # printF(' 134 y: ', y)
            #printF('x; y: ', x, y)
            gpioIN = Pin(int(y), Pin.OUT, Pin.PULL_UP)
            gpioIN.on()
            gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
        
    printF('gpioINput: ', gpioInput, 'curButMap: ', curButMap)
    gc.collect()

    
async def testLeds():
    but1 = Pin(16, Pin.OUT, Pin.PULL_DOWN)
    but2 = Pin(17, Pin.OUT, Pin.PULL_DOWN)
    while True:
        but1.on()
        but2.off()
        await asyncio.sleep(1)
        but1.off()
        but2.on()
    gc.collect()


curGpioState = ''

def getGPIOState(pin):
    #print(' new getGPIOState 156')
    global curGpioState,gpioState, gpioIN, curButMap
    gpioIN.irq(handler=None)
    pinNum = str(pin)[8:10]
    #print("Pin went high: ", pinNum)
    gpioState = ''

    for x in curButMap:
        for y in x.split(','):
            if int(y) == 0:
                gpioState += '0'
            else:
                pin = Pin(int(y), Pin.OUT, Pin.PULL_UP)
                if pin.value() == 1:
                    gpioState += '0'
                else:
                    gpioState += '1'
                    
    #print(f'curGpioState: {curGpioState}  new gpioState: {gpioState}') # current_button_state00000000
    
    if curGpioState != gpioState:
        #print('Different state')
        curGpioState = gpioState
        #print('curGpioState: ', curGpioState)
        gpioIN.irq(handler=getGPIOState)
        sendGPIOUpdate(gpioState)
    #else:
      #  print('same states')
    
 
    gc.collect()

current_button_state = ''



gpioState = ''

currentClientLEDPin = ''
def sendGPIOUpdate(state):
    global clients
    if state is not None:
        # Function to send POST requests to all connected clients
       # print(f"  Sending to clients {clients} ")
        tryCounter = 0
        global currentClientLEDPin
        for ip in clients.keys():
            currentClientLEDPin = config.items("tallyLEDStatus")["tally"+clients[ip]].split(',')[0]
            gc.collect()   
            asyncio.run(sendTo1Client(state, clients, ip, int(clients[ip])))
    gc.collect()

async def setBrightness(red, green, blue, ip,):
            tryCounter = 0 
            while True:
                try:
                    gc.collect()
                    tryCounter += 1
                    # sending Post to IP and endpoint URL from config file with the red, green, blue values
                    url = f"http://{ip}:8080" + config.items('api')['setTallyBrightness']  # Replace with your client's endpoint
                    headers = {'red':red, 'green':green, 'blue':blue}
                    response = requests.post(url,headers=headers,timeout = 1)

                    if response.status_code != 200:
                        await asyncio.sleep(.3)
                        if tryCounter > 5:
                            gc.collect()
                            break

                except Exception as e:
                    gc.collect()
                    await asyncio.sleep(.3)
 
async def sendTo1Client(state, clients, ip,tallyIDForThisIP):
           # print('    cliendIDForThisIP: ', cliendIDForThisIP, 'currentClientLEDPin: ',currentClientLEDPin)
            tryCounter = 0 
            while True:
                try:
                    gc.collect()
                    tryCounter += 1
                  #  print(f"        Sending to {ip}")
                    # Replace with your actual function to send POST requests (e.g., using sockets)
                    url = f"http://{ip}:8080/led"  # Replace with your client's endpoint
                    headers = {'ledStatus':str(state)}
                    response = requests.post(url,headers=headers,timeout = 1)

                    status = response.status_code

                   # print(f'status: {status} | response: {response.text}')
                    #status: ('status: ', 200, 'response: ', '(16, 500, 45000)(18, 500, 0)(17, 500, 0)')
                    if status != 200:
                        await asyncio.sleep(.3)
                     #   print("        trying again: , tryCounter")
                        if tryCounter > 5:
                         #   print(f"             {ip} is not avaialable, errdor: {e}, removing from clients",ip,currentClientLEDPin)
                            del clients[ip]
                            setNeo((0,0,0), 0, tallyIDForThisIP - 1)

                            gc.collect()
                            break

                        #await asyncio.sleep(2)
                    break
                except Exception as e:
                    gc.collect()
                 #   print(f'           ln138 {e} ID: {cliendIDForThisIP}')
                    await asyncio.sleep(.3)
                    if tryCounter > 5:
                   #
                #   print(f"\n            {ip} is not avaialable, errdor: {e}, removing from clients \n")
                        del clients[ip]
                        setNeo((0,0,0), 0, tallyIDForThisIP - 1)

                        gc.collect()
                        break
   

####### baseAPI #################
# recvSetup
@app.post('/recvSetup')
async def create_client(request):
    gc.collect()

    #  print("#############################  NEW CLIENT: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'], " | URL: ", request.url)
    
    clients[request.headers['ip']] = request.headers['tallyID'] 
    
    tallyID = "tally"+request.headers['tallyID']

    bright = int(config.items('tallyLEDStatus')[tallyID]) 
    setNeo(blue, bright, tallyID - 1)

    # print('All Clients: ', clients)
     
    gc.collect()
    return current_button_state, 200, {'Content-Type': 'text/html'}
 

      
@app.route('/', methods=['GET', 'POST'])
async def index(request):
    global config
    gc.collect()

    if request.method == 'POST':
       # print("POST: ", request.url)
        for section in config.sections():
            #print('section: ', section)
            for key in config.options(section):
                form_key = f"{section}_{key}"  # Composite key for each field in the form
                gc.collect()
                if form_key in request.form:
                    
                    #Checking if field is diff from saved field, if is pass if diff update config
                    if config.items(section)[key] == request.form[form_key]:
                        pass
                        #print(request.form[form_key], ' SAME')
                    else:
                        #print(request.form[form_key], ' DIFFFFF')
                        config.set(section, key, request.form[form_key])
            
        #name.write('config.ini')
        gc.collect()
        config.write('baseConfig.json')
        return await Template('index.html').render_async(name=config)
    elif request.method == 'GET':
       # print("Get on: ", request.url)
        gc.collect()
 
 
        return await Template('index.html').render_async(name=config)


   # return config


Response.default_content_type = 'text/html'


@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

    
async def mainThreads():
    #task2 = asyncio.create_task(app.run(debug=True)())
    #asyncio.create_task(blink(14, 2))
   # asyncio.create_task(main_loop())

    #asyncio.create_task(testLeds())
    #app.run has to be last and .run
    gc.collect()
    asyncio.run(app.run(debug=True))
    gc.collect()



# Main program execution
if __name__ == "__main__":
    printFF("ln 366 staritng getConfig")
    
    config, baseStation = getConfig() #GC Done
    
    setupMappings(config) #GC Done
    gc.collect()
    
    #seutp Wifi or AP mode
    myIP = mainFunc(config,baseStation) # GC Done
    printFF(myIP)
    
    gc.collect()
    #make hostname.local available
    responder(announce_service(myIP)) # GC Done
    gc.collect()
    
   # responder(resp)
    
    gc.collect()
 
    asyncio.run(mainThreads())