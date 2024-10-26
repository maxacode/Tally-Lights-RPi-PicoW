
    
    
from machine import Pin
import time

but1 = 16
but2 = 17

# Interrupt handler function
def button_handler(pin):
    button.irq(handler=None)
    print("Button was pressed!", pin)
    x = 0
    while x < 4:
        x +=1
        print('butt handler: ',x, str(pin)[8:10])
        time.sleep(.1)
    time.sleep_ms(200)
    button.irq(handler=button_handler)
    
allButs = but1, but2
for x in allButs:
    # Set up GPIO 14 as an input with a pull-down resistor
    button = Pin(x, Pin.IN, Pin.PULL_DOWN)

# Attach an interrupt to the pin
#button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)
    button.irq(trigger=Pin.IRQ_RISING, handler=button_handler, hard=False)



# Main loop
x = 0
while True:
    x += 1
    print('true: ',x)
    time.sleep(1)  # Keep the loop running

    
