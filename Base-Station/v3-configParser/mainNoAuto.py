"""
base-Station - Main: v1.7

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
    - ledPWM: Function to handle the PWM for the LED pins.
    - setupMappings: Function to setup the GPIO mappings based on the configuration.
    


    """


import time, socket, network, json, requests, asyncio, uasyncio, gc
from machine import Pin, PWM

## External Files:
from getConfig import getConf

from microdot import Microdot, send_file, Response
from utemplate import Template

from cors import CORS

from mdns_client import Client
from mdns_client.responder import Responder
 
from connectToWlan import mainFunc

# Config file to read data

configFileName = 'baseConfig.json'

config = getConf(configFileName)

#print(config)
#print(config.sections())
   

#tallyEnabled = []
current_button_map = []
def setupMappings():
    global current_button_map, hostName
    tallyEnabled = (list(config.items('tallyEnabled').values()))
    y = 1
    gpioInput = config.items('gpioInput')
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    for x in tallyEnabled:
        if x:
            current_button_map.append(gpioInput['tally'+str(y)])
        elif x == False:
            current_button_map.append([0,0])
        y += 1
    #current map [[16, 17], [18, 19], [20, 21], [22, 26]]
 

# function to handle PIN PWM for LED
# neo pixel eventually
def ledPWM(pin, level):
    global output
    #print('Pin: ', pin, 'Freq: ', freq, 'Duty: ', duty)
    pinLed = Pin(int(pin))
    pinLedPWM = PWM(pinLed)
    pinLedPWM.freq(500)
    pinLedPWM.duty_ns(int(level))
    #print("returning pin freq duty")
    return f"(ledPWM: {pin}, {level})"

for x in (12,13,14,15):
    ledPWM(x, 0)

def announce_service(baseIP):
    client = Client(baseIP)
    #print(config.items('global')['baseStationName'])
    
    responder = Responder(
        client,
        own_ip=lambda: baseIP,
        host=lambda: config.items('global')['baseStationName'])
    
    return responder
    #responder.advertise()

    # If you want to set a dedicated service host name
   

def responder(responder):
    responder.advertise("tallyAdver8080", "_hello._tcp", port=8080, data={"tallySetup": "/recvSetup"})



 
####### API ######################
app = Microdot()
CORS(app, allowed_origins='*', allow_credentials=True)

clients = {}
current_button_state = []  # Initialize global variable for button state

curButMap = []
def setupIRQ():
    global gpioIN,curButMap
    tallyEnabled = config.items('tallyEnabled').values() # tallyEnabled:  dict_values(['true', 'true', 'true', 'true'])
    y = 1
    gpioInput = config.items('gpioInput') #gpioInput:  {'tally1': '17, 16', 'tally4': '26, 22', 'tally3': '21, 20', 'tally2': '19, 18'}

    for x in tallyEnabled:
        if x:
            curButMap.append(gpioInput['tally'+str(y)])
        elif x == False:
            curButMap.append([0,0])
        y += 1
    #print('cur but map: ', curButMap) # cur but map:  ['17, 16', '19, 18', '21, 20', '26, 22']

    for x in curButMap:
        #print('x2: ', x)
        for y in x.split(','):
            #print(' 134 y: ', y)
            #print('x; y: ', x, y)
            gpioIN = Pin(int(y), Pin.OUT, Pin.PULL_UP)
            gpioIN.on()
            gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
        
    #print('gpioINput: ', gpioInput, 'curButMap: ', curButMap)
    
    
async def testLeds():
    but1 = Pin(16, Pin.OUT, Pin.PULL_DOWN)
    but2 = Pin(17, Pin.OUT, Pin.PULL_DOWN)
    while True:
        but1.on()
        but2.off()
        await asyncio.sleep(1)
        but1.off()
        but2.on()

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
            gc.collect()
                        
            cliendIDForThisIP  = clients[ip]
            currentClientLEDPin = config.items("tallyLEDStatus")["tally"+clients[ip]].split(',')[0]
            
            asyncio.run(sendTo1Client(state, clients, ip,cliendIDForThisIP,currentClientLEDPin ))

async def sendTo1Client(state, clients, ip,cliendIDForThisIP,currentClientLEDPin):
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
                            ledPWM(int(currentClientLEDPin), 0)
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
                        ledPWM(int(currentClientLEDPin), 0)
                        gc.collect()
                        break
                

####### baseAPI #################
# recvSetup
@app.post(config.items('api')['receiverSetup'])
async def create_client(request):
    gc.collect()

    #  print("#############################  NEW CLIENT: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'], " | URL: ", request.url)
    
    clients[request.headers['ip']] = request.headers['tallyID'] 
    
    tallyID = "tally"+request.headers['tallyID']

    tallyID2 = int(config.items('tallyLEDStatus')[tallyID].split(',')[0])
    bright = int(config.items('tallyLEDStatus')[tallyID].split(',')[1]) 
    ledPWM(tallyID2, bright)

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
    asyncio.run(app.run(debug=True))



# Main program execution
if __name__ == "__main__":
    # config = getConf() runs first to setup files
    #print("SetupMappings()")
    setupMappings()
    gc.collect()
    
    #seutp Wifi or AP mode
    baseIP = mainFunc(configFileName)
    gc.collect()
    #make hostname.local available
    resp = announce_service(baseIP)
    gc.collect()
    responder(resp)
    gc.collect()

    #setup pins to be interupted based on config file
    setupIRQ()
    gc.collect()
    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute





