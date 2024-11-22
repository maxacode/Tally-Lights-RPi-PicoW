# Control NP with a function v2 bpiMicropython
# Usage: setNeo(color, level)
# where color is a tuple of RGB values and level is the brightness level

from machine import Pin
from neopixel import NeoPixel

numpix = 5
pin_10 = Pin(10)
np = NeoPixel(pin_10, numpix,bpp=3, timing=1)

red = (128, 0, 0)
green = (0, 128, 0)
blue = (0, 0, 128)
white = (40, 40, 40)
off = (0,0,0)

# have a dictionary with all ID's as Key and value as a list of current colors set. Then do this:
#combined_tuple = tuple(a + b for a, b in zip(tuple1, tuple2))

def setNeo(color, level = 100, id = 0, reset = False):
    """This function adds two numbers together."""
    if reset:
        for x in range(0, numpix):
            np[x] = (0,0,0)
    np[id] = color
    #allColors.append(np.__getitem__(0))
    np.write()
    return color, level, id, reset   
    

if __name__== '__main__':
    setNeo(red, 100, 0)
    setNeo(white, 100, 3, True)
    setNeo(blue, 100, 2)

 


