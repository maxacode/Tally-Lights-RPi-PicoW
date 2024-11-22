import time, board, neopixel


red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

#https://docs.circuitpython.org/projects/neopixel/en/latest/api.html#neopixel.NeoPixel.brightness
# setNeo(color = tuple 3 RGB values, level = brightness 0 - 1(Full), id = pixel number. 
def setNeo(color, level, idN = 0, reset=False):
    npPin = board.GP28
    np = neopixel.NeoPixel(npPin, 5, auto_write = True)

    if reset:
        np.fill((0,0,0))
    np[idN] = color
    np.brightness = level
       
    np.show()
    np.deinit()
    return color, level   
    

if __name__== '__main__':
    while True:
        for x in range(0, 5):
            for y in range(50,200,40):
                setNeo((y,0,y), 1, x)
                setNeo(red, 1, 2)
                
 