"""
base-Station - Main: v1.5

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



configFileName = 'baseConfig.json'
global config
with open(configFileName,'r') as f:
    config = json.load(f)
    #print(config)
    print(config["global"]["version"])

   # smaple button_pin = config['global']['version']
tallyEnabled = []
current_button_map = []
def setupMappings():
    global current_button_map, hostName
    tallyEnabled = (list(config['tallyEnabled'].values()))
    y = 1
    gpioInput = config['gpioInput']
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    #print('gpioinput',gpioInput) 
    for x in tallyEnabled:
        if x:
            
            current_button_map.append(gpioInput['tally'+str(y)])
        elif x == False:
            current_button_map.append([0,0])
        y += 1
        
    # Tally LED Mappings
    
    #current map [[16, 17], [18, 19], [20, 21], [22, 26]]
    #print('current map',current_button_map)


# function to handle PIN PWM for LED
def ledPWM(pin, level):
    global output
    #print('Pin: ', pin, 'Freq: ', freq, 'Duty: ', duty)
    pinLed = Pin(pin)
    pinLedPWM = PWM(pinLed)
    pinLedPWM.freq(500)
    pinLedPWM.duty_ns(level)
    #print("returning pin freq duty")
    return f"(ledPWM: {pin}, {level})"

# files on the devie
from microdot import Microdot, send_file
from cors import CORS

from mdns_client import Client
from mdns_client.responder import Responder
 
#apWorks or wlan
####### setup AP ######################
 


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
        import connectToWlan
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
CORS(app, allowed_origins=['*'], allow_credentials=True)

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
            gpioIN = Pin(y, Pin.IN, Pin.PULL_DOWN)
            gpioIN.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=getGPIOState, hard=False)
        

async def testLeds():
    but1 = Pin(16, Pin.OUT, Pin.PULL_DOWN)
    but2 = Pin(17, Pin.OUT, Pin.PULL_DOWN)
    while True:
        but1.on()
        but2.off()
        await asyncio.sleep(1)
        but1.off()
        but2.on()

def getGPIOState(pin):
    global gpioState
    global gpioIN, curButMap
    print("Pin went high: ", str(pin)[8:10])
    gpioIN.irq(handler=None)
    gpioState = ''
    for x in curButMap:
        #  print('x',x)
        for y in x:
            #  print('y',y)
            if y == 0:
                gpioState += '0'
            else:
                pin = Pin(y, Pin.IN, Pin.PULL_DOWN)
                gpioState += str(pin.value())
    print(f'current_button_state{curButMap}  new state {gpioState}') # current_button_state00000000
    gpioIN.irq(handler=getGPIOState)
    
    sendGPIOUpdate(gpioState)
 
 
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
          print('currentClientLEDPin: ',currentClientLEDPin)
                
          while True:
            try:
                tryCounter += 1
                print(f"Sending to {ip}")
                # Replace with your actual function to send POST requests (e.g., using sockets)
                url = f"http://{ip}:8080/led"  # Replace with your client's endpoint
                headers = {'ledStatus':str(state)}
                response = requests.post(url,headers=headers,timeout = 1)
                gc.collect()
                
                currentClientLEDPin = config["tallyLEDStatus"]["tally"+clients[ip]][0]
                print('currentClientLEDPin: ',currentClientLEDPin)
                
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
                
           

########### Main Loop #################
#async def main_loop():
    
    #print("Main Loop")
    #while True:
        #new_state = get_button_state()
        #if new_state is not None:
        #    send_button_update(new_state)
       # await asyncio.sleep(0.3)  # Adjust sleep time as needed


####### baseAPI #################
        
@app.post(config['api']['receiverSetup'])
async def create_client(request):
  #  print("requests.headers.ip: ", request.headers['ip'])
  #  print("requests.headers.tallyID: ", request.headers['tallyID'])
    print("#############################  NEW CLIENT: ", request.headers['ip'], "| Tally ID: ", request.headers['tallyID'], " | URL: ", request.url)
    #requests.url:  /recvSetup?test123=hello123
    #print("requests.json: ", request.json)
   # print("requests.form: ", request.form)
    
    # add client it 
    clients[request.headers['ip']] = request.headers['tallyID'] 
    
    #print('config',config['tallyLEDStatus'])
    tallyID = "tally"+request.headers['tallyID']

    tallyID2 = config['tallyLEDStatus'][tallyID][0]
    
    #print('tallyID2',tallyID2)

    
    print(ledPWM(tallyID2, config['tallyBrightness'][tallyID]))

    print('All connected Clients: ', clients)
    # Start the main loop after adding a client
   # task1 = asyncio.create_task(main_loop())
    
    return current_button_state, 200, {'Content-Type': 'text/html'}
    #print("Starting thread main_loop()")

   # main_loop()

   # finally:
       # _thread.start_new_thread(main_loop())
        #main_loop()

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
    jsonReq = "configUpdate:json ", request.json
    print('jsonreq',jsonReq)
   # print('jsonred[email',jsonReq[1]['age'])
    for x in jsonReq[1].keys():
        print('x',x)
        print(config['global'][x])
        print(jsonReq[x])
        #key1 = "['global"+"[{x}]"
        updateConfig(x,jsonReq[x])
        #updateConfig(x,jsonReq[1][x])
   # print("configUpdate: txt ", request.text)
    #print("configUpdate: headers ", request.headers)


    # return JSON response with word 'Config Updated' and status code 200
    return {'message': 'Config Updated'}, 200

@app.route('/')
async def home(request):
    response = send_file('indexTest.html')
    return response


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
    setupMappings()
    
    #seutp Wifi or AP mode
    baseIP = setupWLAN()
    resp = announce_service(baseIP)
    responder(resp)

    
    setupIRQ()

    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute






