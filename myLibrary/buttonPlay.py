from machine import Pin
from time import sleep

but = Pin(16, Pin.IN, Pin.PULL_UP)

while True:
    if but.value() == 0:
        print("Button Pressed")
    elif but.value() == 1:
        print("Button Released")
    else:
        print("Button Error")
    sleep(0.5)