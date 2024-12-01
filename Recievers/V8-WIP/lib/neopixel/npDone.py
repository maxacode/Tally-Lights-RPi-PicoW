# Control NP with a function v2
# Usage: setNeo(color, level)
# where color is a tuple of RGB values and level is the brightness level

from lib.neopixel.neopixel import Neopixel

# numpix = 1
strip = Neopixel(5, 0, 28, "RGB")

green = (255, 0, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
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
    setNeo((0,255,0),80,0,True)
    setNeo((255,255,0),100, 2,True)
#     setNeo((0,0,255),30,1)
#     setNeo((255,0,0),30,2)
#     setNeo((255,255,0),30,3)
#     setNeo((255,0,100),30,4)

