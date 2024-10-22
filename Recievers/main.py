# Test LED

from machine import Pin, PWM
from time import sleep
import asyncio
import requests

import connectToWlan
myIP = connectToWlan.connectWLAN()

from microdot import Microdot, send_file
app = Microdot()

print(1.2)
# function to handle PIN PWM for LED
def ledPWM(pin, freq, duty):
    global output
    print('Pin: ', pin, 'Freq: ', freq, 'Duty: ', duty)
    pinLed = Pin(pin)
    pinLedPWM = PWM(pinLed)
    pinLedPWM.freq(freq)
    pinLedPWM.duty_ns(duty)
    print("returning pin freq duty")
    return f"({pin}, {freq}, {duty})"

@app.route('/')
async def hello(request):
    response = send_file('index.html')
    return response
    #return html, 200, {'Content-Type': 'text/html'}

@app.post('/led')
async def led(request):
    # turn on led 16 half brightness
    ledStatus = str(request.headers['ledStatus'])
    print(f"ledStatus: {ledStatus}")
    if ledStatus == '1':
        out = ledPWM(16, 500, 19000)
        out2 =  str(myIP + out)
    elif ledStatus == '0':
        out = ledPWM(16, 500, 0)
        out2 =  str(myIP + out)
    else: 
        out2 =  str(myIP + ' Invalid LED Status')
    return out2, 200, {'Content-Type': 'text/html'}




@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

async def recvSetup():
    # Sending a post to base and recvSetup with IP and Tally ID
    url = 'http://192.168.88.234:8080/recvSetup'
    tallyID = '01'
    print(myIP)

    headers = {'ip':myIP, 'tallyID':tallyID}
    print('sending post')
    response = requests.post(url,headers=headers)
    print('post sent')
    if response.status_code == 200:
        print('Request successful')
        print(response)
    else:
        print('Request failed')
        print(response)

    
async def mainThreads():
    print(1.7)
    #task2 = asyncio.create_task(app.run(debug=True)())
    asyncio.create_task(recvSetup())
    #app.run has to be last and .run
    asyncio.run(app.run(debug=True))


# Main program execution
if __name__ == "__main__":
    asyncio.run(mainThreads())
    # Main thread continues running while the other threads execute
    print("xyz")
 