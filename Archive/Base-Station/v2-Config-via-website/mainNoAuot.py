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
config = getConf()
    

#tallyEnabled = []
current_button_map = []
def setupMappings():
    global current_button_map, hostName
    tallyEnabled = (list(config['tallyEnabled'].values()))
    y = 1
    gpioInput = config['gpioInput']
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
    pinLed = Pin(pin)
    pinLedPWM = PWM(pinLed)
    pinLedPWM.freq(500)
    pinLedPWM.duty_ns(level)
    #print("returning pin freq duty")
    return f"(ledPWM: {pin}, {level})"


def setupWLAN():
    apMode = config['global']['apMode']
    
    if apMode:
        import apWorks
        ssid = config['global']["apSSID"]
        print("Starting in AP Mode with SSID: ", ssid)
        ssidPassword = config['global']["apPassword"]
        apWorks.setup_ap(ssid,ssidPassword)
    elif apMode == False:
        print("Connecting to WLAN")
        ssid = config['global']["wlanSSID"]
        ssidPassword = config['global']["wlanPassword"]
        baseIP = connectToWlan.connectWLAN(ssid,ssidPassword)
        print(baseIP)
    y = 0
    while y < 10:
        for x in config['tallyLEDStatus'].values():
            z = 50000
            ledPWM(x[0],z)
            time.sleep(.20)
            z = 0
            ledPWM(x[0],z)
            y += 1
            
    return(baseIP)




def announce_service(baseIP):
    client = Client(baseIP)
    print(config['global']['baseStationName'])
    
    responder = Responder(
        client,
        own_ip=lambda: baseIP,
        host=lambda: config['global']['baseStationName'])
    
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
    tallyEnabled = (list(config['tallyEnabled'].values()))
    y = 1
    gpioInput = config['gpioInput']
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    #print('gpioinput',gpioInput) 
    for x in tallyEnabled:
        if x:
            curButMap.append(gpioInput['tally'+str(y)])
        elif x == False:
            curButMap.append([0,0])
        y += 1
    for x in curButMap:
        for y in x:
            #print('x; y: ', x, y)
            gpioIN = Pin(y, Pin.OUT, Pin.PULL_UP)
            gpioIN.on()
            gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState)
        
    print('gpioINput: ', gpioInput, 'curButMap: ', curButMap)
    
    
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
    global curGpioState,gpioState, gpioIN, curButMap
    gpioIN.irq(handler=None)
    pinNum = str(pin)[8:10]
    print("Pin went high: ", pinNum)
    gpioState = ''

    for x in curButMap:
        #  print('x',x)
        for y in x:
            #  print('y',y)
            if y == 0:
                gpioState += '0'
            else:
                pin = Pin(y, Pin.OUT, Pin.PULL_UP)
                if pin.value() == 1:
                    gpioState += '0'
                else:
                    gpioState += '1'
    print(f'curGpioState: {curGpioState}  new gpioState: {gpioState}') # current_button_state00000000
    
    if curGpioState != gpioState:
        print('Different state')
        curGpioState = gpioState
        print('curGpioState: ', curGpioState)
        gpioIN.irq(handler=getGPIOState)
        sendGPIOUpdate(gpioState)
    else:
        print('same states')
    
 
 
current_button_state = ''



gpioState = ''


currentClientLEDPin = ''
def sendGPIOUpdate(state):
    if state is not None:
        # Function to send POST requests to all connected clients
        #headers = {"button_state": state}  # Create JSON data for the POST request
        print(f"Sending to clients {clients} | state: {state}")
        tryCounter = 0
        #clients {'192.168.88.247': '1'}
        global currentClientLEDPin
        for ip in clients.keys():
          currentClientLEDPin = config["tallyLEDStatus"]["tally"+clients[ip]][0]
          #print('currentClientLEDPin: ',currentClientLEDPin)
                
          while True:
            try:
                tryCounter += 1
                print(f"Sending to {ip}")
                # Replace with your actual function to send POST requests (e.g., using sockets)
                url = f"http://{ip}:8080/led"  # Replace with your client's endpoint
                headers = {'ledStatus':str(state)}
                response = requests.post(url,headers=headers,timeout = 5)
                gc.collect()
                
                currentClientLEDPin = config["tallyLEDStatus"]["tally"+clients[ip]][0]
               # print('currentClientLEDPin: ',currentClientLEDPin)
                
               # print(f"currentClientLEDPin: {currentClientLEDPin}")
                status = response.status_code

                print(f'status: {status} | response: {response.text}')
                #status: ('status: ', 200, 'response: ', '(16, 500, 45000)(18, 500, 0)(17, 500, 0)')
                if status != 200:
                    print(f"{ip} is not avaialable | status: {status} | removing from clients",ip,currentClientLEDPin)
                    del clients[ip]
                    ledPWM(currentClientLEDPin, 0)

                    #await asyncio.sleep(2)
                break
            except Exception as e:
                print(f'ln138 {e}')
                if tryCounter > 2:
                    print(f"{ip} is not avaialable, errdor: {e}, removing from clients",ip,currentClientLEDPin)
                    del clients[ip]
                    ledPWM(currentClientLEDPin, 0)
                    break
                

####### baseAPI #################
        
@app.post(config['api']['receiverSetup'])
async def create_client(request):
  #  print("requests.headers.ip: ", request.headers['ip'])
  #  print("requests.headers.tallyID: ", request.headers['tallyID'])
    print("#############################  NEW CLIENT: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'], " | URL: ", request.url)
    #print("requests.json: ", request.json)
   # print("requests.form: ", request.form)
    
    clients[request.headers['ip']] = request.headers['tallyID'] 
    
    tallyID = "tally"+request.headers['tallyID']

    tallyID2 = config['tallyLEDStatus'][tallyID][0]
 
    print(ledPWM(tallyID2, config['tallyBrightness'][tallyID]))

    print('All connected Clients: ', clients)
     
    
    return current_button_state, 200, {'Content-Type': 'text/html'}
 

def write_config(config):
    try:
        with open(configFileName, "w") as file:
            json.dump(config, file)
            print("Config saved:", config)

    except Exception as e:
        print("Error writing config file:", e)


def updateConfig(key,value):
        # Load the current config


    # Update the key with the new value
    config['global'][key] = value

    # Save the updated config
    write_config(config)

      
#@app.post('/configUpdate')
@app.route('/configUpdate', methods=['POST', 'OPTIONS'])
async def configUpdate(request):
    #jsonReq = "configUpdate:json ", request.json
    jsonReq = request.json
    print('jsonreq',jsonReq)
   # print('jsonred[email',jsonReq[1]['age'])
    for x in jsonReq.keys():
        print('x: ' ,x)
       # print(config['global'][x])
      #  print(jsonReq[x])
        #key1 = "['global"+"[{x}]"
        #updateConfig(x,jsonReq[x])
        #updateConfig(x,jsonReq[1][x])
   # print("configUpdate: txt ", request.text)
    #print("configUpdate: headers ", request.headers)


    # return JSON response with word 'Config Updated' and status code 200
    return {'message': 'Config Updated'}, 200



@app.route('/', methods=['GET', 'POST'])
async def index(req):
    global config
    #name = None
    #if req.methodest  == 'POST':
      #  name3 = config
    #response = send_file('indexTest.html')
    # Sends the conifg var which is conents of config file
    
    if req.method == 'POST':
        print("POST: ", req.url)
        #print(req)
        #print(req.form.get('api')['ledControlEndpoint'])
        #print(req.form)
        config2 = req.json
        
        
        with open("sampleConf.json", 'w') as x:
            json.dump(config2, x)
            
       # print(config2)
        return await Template('index.html').render_async(name=config2)
    elif req.method == 'GET':
        print("Get on: ", req.url)
        with open("sampleConf.json", 'r') as f:
            config2 = json.load(f)
        
        print(config2)
        print('get on: ', req.url)
    
    return await Template('index.html').render_async(name=config2)


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

    setupMappings()
    
    #seutp Wifi or AP mode
    baseIP = mainFunc()
    #make hostname.local available
    resp = announce_service(baseIP)
    responder(resp)

    #setup pins to be interupted based on config file
    setupIRQ()

    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute






