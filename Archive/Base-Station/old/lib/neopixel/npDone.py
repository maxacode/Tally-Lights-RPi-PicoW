# Control NP with a function v2
# Usage: setNeo(color, level)
# where color is a tuple of RGB values and level is the brightness level

from lib.neopixel.neopixel import Neopixel

# numpix = 1
strip = Neopixel(4, 0, 28, "RGB")

# green = (255, 0, 0)
# red = (0, 255, 0)
# blue = (0, 0, 255)
# white = (255, 255, 255)


def setNeo(color, level, id = 0):
    """This function adds two numbers together."""
    strip.brightness(level)
    strip.set_pixel(id, color)
    strip.show()
    strip.fill((0,0,0))
    return color, level   
    

if __name__== '__main__':
    setNeo((255,0,0),30)
    