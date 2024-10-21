# Test LED

from machine import Pin, PWM
from time import sleep
import connectToWlan
connectToWlan.connectWLAN()

from microdot import Microdot, send_file
app = Microdot()


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

@app.route('/led16on')
async def led16on(request):
    # turn on led 16 half brightness
    out = ledPWM(16, 500, 19000)
    return out, 200, {'Content-Type': 'text/html'}

@app.route('/led16off')
async def led16off(request):
    # turn on led 16 half brightness
    out = ledPWM(16, 500, 0)
    return out, 200, {'Content-Type': 'text/html'}



@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


app.run(debug=True)
