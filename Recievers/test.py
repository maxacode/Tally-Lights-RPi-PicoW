"""
v1.1 11/20
- colors and setNeo are mapped to np so they dont need to be prefixed with np.
- 
"""
from lib.neopixel.npTestClass import NeoPixelController

# Create a NeoPixelController instance with a brightness level of 100
#controller = NeoPixelController(brightness_level=100)

# Shorter way.  and not specificing defualt birhgtness
np = NeoPixelController()
setNeo = np.setNeo

# this way works but then every file would need it instead of just passing NP object to each other file func and getting colors liek that.

#green, red, blue, white, off = np.green, np.red, np.blue, np.white, np.off

setNeo(np.green)

from test2 import sayHi
from time import sleep
sleep(.1)

# this works but on sayHi fucnt hey have to do colors['blue'] but np.blue is easier
colors = {
    "green": np.green,
    "red": np.red,
    "blue": np.blue,
    "white": np.white,
    "off": np.off
}

# Pass the NeoPixelController instance and the colors to sayHi
sayHi(np, colors, sleep)


# Use the controller to set NeoPixel colors - longer way
#controller.set_neo(controller.white, reset=True)  # Set first pixel to green
#result = controller.set_neo((255, 255, 0), level=100, pixel_id=2)  # Set third pixel to yellow
#print(result)  # Output the result

