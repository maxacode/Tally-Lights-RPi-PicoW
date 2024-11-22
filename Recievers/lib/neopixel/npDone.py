# Control NP with a function v2
# import from lib.npDone import setNeo, red, green, blue, white, off
# Usage: setNeo(color, level)
# where color is a tuple of RGB values and level is the brightness level

from lib.neopixel.neopixel import Neopixel

numpix = 5
pinNum = 28
state_machine = 0 # alwyas 0
mode = "RGB" # add W for those Leds
strip = Neopixel(numpix, 0, pinNum, mode)

red = (128, 0, 0)
green = (0, 128, 0)
blue = (0, 0, 128)
white = (40, 40, 40)
off = (0,0,0)


def setNeo(color, level, id = 0, reset = False):
    """This function adds two numbers together."""
    if reset:
        strip.fill((0,0,0))
        
    strip.brightness(level)
    strip.set_pixel(id, color)
    strip.show()
    return color, level, id, reset   
    

if __name__== '__main__':
    print(setNeo(red,80,0))
    setNeo(green,100, 2)
#     setNeo((0,0,255),30,1)
#     setNeo((255,0,0),30,2)
#     setNeo((255,255,0),30,3)
#     setNeo((255,0,100),30,4)
