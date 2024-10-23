"""
This is the main script for the base station API. It is responsible for handling the API requests and sending updates to the clients.
Functions and classes:
    
    - get_button_state: Function to read the button state from the GPIO pins.
    - send_button_update: Function to send the button state to all connected clients.
    - main_loop: Main loop function to continuously check for button state changes and send updates.
    - create_client: API endpoint to add a new client to the list of connected clients.
    - shutdown: API endpoint to shutdown the server.
    """
import time, socket, network
print("vtempMain: 1.5")
#from time import sleep
from machine import Pin
import json  # Import for JSON formatting
import requests
import _thread
import asyncio

# files on the devie
from microdot import Microdot
import connectToWlan
from picozero import LED


####### setup AP ######################

apMode = False

if apMode == True:
    import apWorks
    apWorks.setup_ap()
elif apMode == False:
    connectToWlan.connectWLAN()

####################################


####### API ######################
app = Microdot()
clients = {}
current_button_state = []  # Initialize global variable for button state


def get_button_state():
    #print("get_button_state")
    global current_button_state
    new_state = []
    t1PST = Pin(16, Pin.IN, Pin.PULL_DOWN)
    t1PGM = Pin(17, Pin.IN, Pin.PULL_DOWN)
    t2PST = Pin(18, Pin.IN, Pin.PULL_DOWN)
    t2PGM = Pin(19, Pin.IN, Pin.PULL_DOWN)

    pin15 = Pin(15, Pin.OUT)

    allTallys = (t1PST,t1PGM,t2PST,t2PGM)
    # x = 0
    # for y in allTallys:
    #     #print(x.value())
    #     new_state.append(allTallys[x].value())
    #     x += 1
    #     new_state.append(allTallys[x].value())
    #     x += 1
   # for x in allTallys:
      #  new_state = new_state + [x.value()]

    new_state = str(t1PST.value())+str(t1PGM.value())+str(t2PST.value())+str(t2PGM.value())+'0000'

    if new_state != current_button_state:
        current_button_state = new_state
        print("Button Changed to:", new_state)
       # groupedTallys = str(zip(str(new_state[::2]),str(new_state[1::2])))
        print(new_state)
        return new_state
    else:
        return None  # Return None if no change detected


def send_button_update(state):
    if state is not None:
        # Function to send POST requests to all connected clients
        #headers = {"button_state": state}  # Create JSON data for the POST request
        print(f"Sending changes to clients state: {state}")
        for ip in clients.keys():
            try:
                print(f"Sending to {ip}")
                # Replace with your actual function to send POST requests (e.g., using sockets)
                url = f"http://{ip}:8080/led"  # Replace with your client's endpoint
                headers = {'ledStatus':str(state)}

                response = requests.post(url,headers=headers,timeout = .5)
                #response = requests.post(url, json=data)  # Use requests library to send POST
                #response.raise_for_status()  # Raise exception for non-200 response codes
                status = response.status_code
                print(f"status: {status}")
                print(response.text)
                if status != 200:
                    print(f"{ip} is not avaialable, status: {status}, removing from clients")
                    print(clients)
                    del clients[ip]
                    print(clients)
                print(f"Sent button state {state} to client at {ip}")
            except Exception as e:
             #   print(f"{ip} is not avaialable, errdor: {e}, removing from clients")
              #  print(clients)
              #  del clients[ip]
                print(f"line 82 {e}")


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

async def blink(led, period_ms):
    #led = Pin(ledd, Pin.OUT)
    while True:
        #print(f"blink1 {led}")
        led.on()
        await asyncio.sleep(2)
        led.off()
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
    asyncio.create_task(blink(LED(14), 2))
    asyncio.create_task(main_loop())
    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":
    


    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    print("xyz")
 

