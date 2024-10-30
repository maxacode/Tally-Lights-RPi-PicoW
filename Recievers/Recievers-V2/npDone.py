#Example 1 - Control individual LED

from neopixel import Neopixel
import utime
import random

numpix = 1
strip = Neopixel(numpix, 0, 28, "RGB")

green = (255, 0, 0)
orange = (100, 200, 0)
yellow = (255, 230, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
violet = (0, 255, 100)

delay = .5
x = 0
blank = (0,0,0)

def setNeo(color, level):
    strip.brightness(level)
    strip.set_pixel(0, color)
    strip.show()
    strip.fill((0,0,0))
    return color, level
    
    
if __name__== '__main__':
    setNeo(red,30)
    