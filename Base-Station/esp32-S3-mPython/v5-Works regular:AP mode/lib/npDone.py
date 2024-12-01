# Control NP with a function v2 bpiMicropython
# 1:29 PM 11/11 VScode
# where color is a tuple of RGB values and level is the brightness level
"""
This is a module to control the NeoPixel on the bpiW-Micro
functions: setNeo(color, level, id, reset)
def setNeo(color:tuple[int,int,int], level:int = 100, id:int = 0, reset: bool = False) -> tuple[tuple,int,int,int]:

"""
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
def setNeo(color:tuple[int,int,int], level:int = 100, id:int = 0, reset: bool = False) -> tuple[tuple,int,int,int]:
    """This function adds two numbers together.
    
    Args: 
        color: tuple of RGB values
        level: brightness level
        id: specific Neopixel ID
        reset: reset all pixels to off

    Returns:
        color: tuple of RGB values
        level: brightness level
        id: specific Neopixel ID
        reset: reset all pixels to off

    """
    if reset:
        for x in range(0, numpix):
            np[x] = (0,0,0) #type: ignore # tunr off all pixels

    np[id] = color #type: ignore
    #allColors.append(np.__getitem__(0)) # get value of specific Neopixel
    np.write()
    return color, level, id, reset   



if __name__== '__main__':
    setNeo(red, 100, 0)
    setNeo(white, 100, 3, True)
    setNeo(blue, 100, 2)

 


