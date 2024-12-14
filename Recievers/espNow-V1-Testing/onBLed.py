"""
from onBLed import lon, loff, tester, ltog

"""
from machine import Pin
import time

# 21 = S3, 15 C6
S3 = 21
C6 = 15

# Define the LED pin
led = Pin(C6, Pin.OUT)  # Use correct gpio


def lon():
    #led = Pin(21, Pin.OUT)  # Use correct gpio
    led.value(0)
    
def loff():
    #led = Pin(21, Pin.OUT)  # Use correct gpio
    led.value(1)
    
def ltog():
    if led.value() == 1:
        led.value(0)
    else:
        led.value(1)
    
# Blink the LED in a loop
def tester()->None:
    """
    test led functionality 
    """
    for x in range(0,4):
        print('led on')
        led.value(1)   # Turn the LED on
        time.sleep(.4)  # Wait for a second
        print('led off')

        led.value(0)   # Turn the LED off
        time.sleep(.1)  # Wait for a second


if __name__ == "__main__":
   # lon()
   # loff()
   # tester()
    ltog()
    
   # tester()


