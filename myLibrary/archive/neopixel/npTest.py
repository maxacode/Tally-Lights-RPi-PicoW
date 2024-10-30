#Example 1 - Control individual LED

from neopixel import Neopixel
import utime

numpix = 1
pinNum = 28
strip = Neopixel(numpix, 0, pinNum, "RGBW")

green = (255, 0, 0)
orange = (255, 50, 0)
yellow = (255, 100, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
indigo = (100, 0, 90)
violet = (200, 0, 100)
colors_rgb = [red, orange, yellow, green, blue, indigo, violet]

#Commands
#    strip.set_pixel(0, blue)
#    strip.show()
#    utime.sleep(delay)
#    strip.fill((0,0,0))  
 #   strip.brightness(brightness)
#blank = (0,0,0)
#strip.fill((0,0,0))
#strip.show()

def setNeo(color,brightness):
    global strip
    #strip.fill((0,0,0))
   # strip.show()
    #strip.set_pixel(0, blank)
    if color not in colors_rgb:
        return f"Color {color} not in List"
    
   # strip.fill((0,0,0))
   # strip.show()
    strip.set_pixel(0, color)
    strip.brightness(brightness)
    strip.show()
    utime.sleep(.4)
   
    
if __name__ == "__main__":
    while True:
        for x in colors_rgb:
            strip.fill((0,0,0))
            strip.show()
            setNeo(x, 300)
   # strip.fill((0,0,0))
   # strip.show()
    