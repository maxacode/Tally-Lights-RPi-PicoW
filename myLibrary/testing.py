
    
    
from machine import Pin
import time

# Interrupt handler function
def button_handler(pin):
    print("Button was pressed!")

# Set up GPIO 14 as an input with a pull-down resistor
button = Pin(16, Pin.IN, Pin.PULL_DOWN)

# Attach an interrupt to the pin
button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)

# Main loop
while True:
    time.sleep(1)  # Keep the loop running

#interups
but1 = 16
but2 = 17

from machine import Pin
from time import sleep

int1 = Pin(but1, Pin.IN, Pin.PULL_DOWN)
int2 = Pin(but2, Pin.IN, Pin.PULL_DOWN)


def intHandler(button):
    print('button number triggered: ',button)


int1.irq(trigger=Pin.IRQ_RISING, handler=intHandler(int1))

x = 0
while True:
    x +=1 
    print("True Loop: ", x)
    sleep(.5)
    
