#Example 1 - Control individual LED

from neopixel import Neopixel
import utime
import random

numpix = 1
strip = Neopixel(numpix, 0, 28, "RGB")

green = (255, 0, 0)
orange = (255, 50, 0)
yellow = (255, 100, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
indigo = (100, 0, 90)
violet = (200, 0, 100)
colors_rgb = [red, orange, yellow, green, blue, indigo, violet]

delay = .5
x = 10
strip.brightness(x)
blank = (0,0,0)

def runNeo(color, level):
    global strip, x
    while True:
        x += 10
        print(x)
        strip.set_pixel(0, blue)
        strip.show()
        utime.sleep(delay)
        strip.brightness(50)
        strip.fill((0,0,0))
        strip.set_pixel(0, red)
        strip.show()
        utime.sleep(delay)
        strip.fill((0,0,0))
        strip.set_pixel(0, green)
        strip.brightness(10)
        strip.show()
        utime.sleep(delay)
        strip.fill((0,0,0))
        print("###########")
        utime.sleep(1)
        strip.brightness(x)
    

runNeo(red, 100)
