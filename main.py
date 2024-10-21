# Test LED

from machine import Pin
import uasyncio
from time import sleep

boardLed = Pin("LED", Pin.OUT)

while True:
    boardLed.toggle()
    sleep(1)