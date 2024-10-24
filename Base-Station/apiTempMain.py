"""
base-Station - Main:

This is the main script for the base station API. It is responsible for handling the API requests and sending updates to the clients.
Functions and classes:
    
    - get_button_state: Function to read the button state from the GPIO pins.
    - send_button_update: Function to send the button state to all connected clients.
    - main_loop: Main loop function to continuously check for button state changes and send updates.
    - create_client: API endpoint to add a new client to the list of connected clients.
    - shutdown: API endpoint to shutdown the server.


    """


import time, socket, network

#from time import sleep
from machine import Pin, PWM
import json  # Import for JSON formatting
import requests
import asyncio

with open('baseConfig.json','r') as f:
    config = json.load(f)
    #print(config)
    print(config["global"]["version"])

   # smaple button_pin = config['global']['version']
tallyEnabled = []
current_button_map = []
def setupMappings():
    global current_button_map
    tallyEnabled = (list(config['tallyEnabled'].values()))
    y = 1
    gpioInput = config['gpioInput']
    # gpioinput {'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
    print('gpioinput',gpioInput) 
    for x in tallyEnabled:
        if x:
            
            current_button_map.append(gpioInput['tally'+str(y)])
        elif x == False:
            current_button_map.append([0,0])
        y += 1
    #current map [[16, 17], [18, 19], [20, 21], [22, 26]]
    #print('current map',current_button_map)

setupMappings()


# files on the devie
from microdot import Microdot
import gc
#apWorks or wlan
####### setup AP ######################

apMode = config['global']['apMode']

if apMode:
    import apWorks
    apWorks.setup_ap()
elif apMode:
    import connectToWlan
    connectToWlan.connectWLAN()

####################################


####### API ######################
app = Microdot()
clients = {}
current_button_state = []  # Initialize global variable for button state

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

current_button_state = ''
def get_button_state():
    #print("get_button_state")
    global current_button_state
    new_state = ''
    for x in current_button_map:
        #  print('x',x)
        for y in x:
            #  print('y',y)
            if y == 0:
                new_state += '0'
            else:
                pin = Pin(y, Pin.IN, Pin.PULL_DOWN)
                new_state += str(pin.value())
   # print(f'current_button_state{current_button_state}') # current_button_state00000000

    if new_state != current_button_state:
        current_button_state = new_state
        #print("Button Changed to:", new_state)
       # groupedTallys = str(zip(str(new_state[::2]),str(new_state[1::2])))
       # print(new_state)
        return new_state
    else:
        return None  # Return None if no change detected


currentClientLEDPin = ''
def send_button_update(state):
    if state is not None:
        # Function to send POST requests to all connected clients
        #headers = {"button_state": state}  # Create JSON data for the POST request
        print(f"Sending to clients {clients} | state: {state}")
        tryCounter = 0
        #clients {'192.168.88.247': '1'}
        global currentClientLEDPin
        for ip in clients.keys():
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
               # print(f"currentClientLEDPin: {currentClientLEDPin}")
                status = response.status_code

                print(f'status: {status} | response: {response.text}')
                #status: ('status: ', 200, 'response: ', '(16, 500, 45000)(18, 500, 0)(17, 500, 0)')
                if status != 200:
                    print(f"{ip} is not avaialable | status: {status} | removing from clients")
                    del clients[ip]
                    ledPWM(currentClientLEDPin, 0)

                    #await asyncio.sleep(2)
                break
            except Exception as e:
                print(f'ln138 {e}')
                if tryCounter > 3:
                    print(f"{ip} is not avaialable, errdor: {e}, removing from clients")
                    del clients[ip]
                    ledPWM(currentClientLEDPin, 0)
                    break
                
                
            #response = requests.post(url, json=data)  # Use requests library to send POST
            #response.raise_for_status()  # Raise exception for non-200 response codes
            #status = response.status_code
                #if status != 200:
             #       print(f"{ip} is not avaialable | status: {status} | removing from clients")
              #      print(clients)
               #     del clients[ip]
                #    print(clients)
                   # await asyncio.sleep(2)
             #   else:
                    
                    #print(f"IP {ip} | status: {status} | response: {response.text} ")
                    #print("sleep 130")
                    #break
                    #await asyncio.sleep(2)
                        
              #  except Exception as e:
               #     print(f"{ip} is not avaialable, errdor: {e}, removing from clients")
                #    del clients[ip]
                 #   print(f"line 134 {e}")


########### Main Loop #################
async def main_loop():
    print("Main Loop")
    while True:
        new_state = get_button_state()
        if new_state is not None:
            send_button_update(new_state)
        await asyncio.sleep(0.3)  # Adjust sleep time as needed


####### baseAPI #################
@app.post('/recvSetup')
async def create_client(request):
    print("requests.headers.ip: ", request.headers['ip'])
    print("requests.headers.tallyID: ", request.headers['tallyID'])
    print("requests.url: ", request.url)
    #requests.url:  /recvSetup?test123=hello123
    print("requests.json: ", request.json)
    print("requests.form: ", request.form)
    
    # add client it 
    clients[request.headers['ip']] = request.headers['tallyID'] 
    
    #print('config',config['tallyLEDStatus'])
    tallyID = "tally"+request.headers['tallyID']

    tallyID2 = config['tallyLEDStatus'][tallyID][0]
    
    #print('tallyID2',tallyID2)

    
    print(ledPWM(tallyID2, config['tallyBrightness'][tallyID]))

    print(clients)
    # Start the main loop after adding a client
    

    print("returingin ack")
    task1 = asyncio.create_task(main_loop())
    
    return current_button_state, 200, {'Content-Type': 'text/html'}
    #print("Starting thread main_loop()")

   # main_loop()

   # finally:
       # _thread.start_new_thread(main_loop())
        #main_loop()
      

@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

async def blink(ledd, period_ms):
    while True:
        #print(f"blink1 {led}")
        ledPWM(ledd, 5000, 15000)
        await asyncio.sleep(2)
        ledPWM(ledd, 5000, 0)
        await asyncio.sleep(period_ms)

async def blink2(led, period_ms):
    #led = Pin(ledd, Pin.OUT)
    while True:
        print(f"blink2 {led}")
        led.on()
        await asyncio.sleep(1)
        led.off()
        await asyncio.sleep(period_ms)

     
    
async def mainThreads():
    #task2 = asyncio.create_task(app.run(debug=True)())
    #asyncio.create_task(blink(14, 2))
    asyncio.create_task(main_loop())
    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":
    


    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    print("xyz")
 



