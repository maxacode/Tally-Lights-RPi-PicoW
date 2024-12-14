
"""
v1.2

    - Creates a controller instance with init
    - chagne brightess
    - default brighess from color-brightness table


    Usage:
    from espNeoPixelClass import setNeo, red, green, blue, white, off, purple
    setNeo(color) # only requires color, level(global default 0-100), pixel id(0), and reset (True) have defaults
    setNeo('green')
    setNeo(white,15,reset = False) # makes a white/green mix
    setNeo((05,25,5), 80) custom RGB values 
    
- to add a new color:
    1. add colorC = RGB value in Define RGB colors section
    2. in color_map add mappings such as "cyan":cynaC
    
v1.2 12/03
- allows reverse compatibaity with existing code as long as imports red/gree, there.


"""



from neopixel import NeoPixel
from machine import Pin

numOfPixels = 5
pinNumber = 44 # GPIO Pin
defaultBrightness = 10

# Define RGB colors
greenC = (0, 255, 0)
redC = (255, 0, 0)
blueC = (0, 0, 255)
whiteC = (255, 255, 255)
offC = (0, 0, 0)
purpleC = (120,0,120)

green = greenC
red = redC
blue = blueC
white = whiteC
off = offC
purple = purpleC


color_map = {
    "green": greenC,
    "red": redC,
    "blue": blueC,
    "white": whiteC,
    "off": offC,
    "purple": purpleC
}


# Global dictionary to store brightness levels for each color
color_brightness = {
    "red": 10,
    "green": 10,
    "blue": 10,
    "white": 15,
}


class NeoPixelController:
    def __init__(self, brightness_level: int = defaultBrightness, num_pixels: int = numOfPixels, pin: int = pinNumber) -> None:
        """Initialize the NeoPixelController with default brightness and configuration."""
        self.strip = NeoPixel(Pin(pin), num_pixels)
        self.default_brightness = brightness_level
        
        self.gr = greenC

    def apply_brightness(self, color, level):
        """Adjust color brightness by scaling RGB values."""
        scale = level / 100
        return tuple(int(c * scale) for c in color)
    
    def blend_colors(self, color1, color2):
        """Blend two RGB colors by averaging their values."""
        return tuple((c1 + c2) // 2 for c1, c2 in zip(color1, color2))
    
    def setNeo(self, color, level=None, pid=0, reset=False) -> tuple:
        """
        Set a NeoPixel to a specific color and brightness level.
        
        Args:
            color (str or tuple): Color name or RGB tuple.
            level (int, optional): Brightness level.
            pixel_id (int, optional): Pixel index to set.
            reset (bool, optional): Clear previous color if True; blend if False.
            
        Returns:
            tuple: (color_with_brightness, pixel_id)
        """
        if reset:
            self.strip.fill(offC)
        
        # Handle color input (name or tuple)
        if isinstance(color, str):  # Color is provided as a string (e.g., "green")

            if color not in color_map:
                print(f"Warning: Color '{color}' not found, using white.")
                color = whiteC
                brightness = self.default_brightness
            else:
                color = color_map[color]
                brightness = level if level is not None else color_brightness.get(color, self.default_brightness)
        else:  # Color is provided as an RGB tuple (e.g., greenC)
            brightness = level if level is not None else self.default_brightness
        
        # Apply brightness to the color
        color_with_brightness = self.apply_brightness(color, brightness)
        
        # Blend colors if reset is False - not useful since we have rset
#         if not reset:
#             current_color = self.strip[pid]
#             color_with_brightness = self.blend_colors(current_color, color_with_brightness)
#         
        # Set the pixel with the adjusted color
        self.strip[pid] = color_with_brightness
        self.strip.write()
        return color_with_brightness, pid

# Create a global instance of the NeoPixelController
_controller = NeoPixelController()

c = _controller
# Expose the setNeo function for direct use
setNeo = _controller.setNeo

#import time

# while True:
#tallyIDStr = 'tally4'
# = '0'

setNeo(green, pid=3)
#     time.sleep(1)
#     setNeo(red, 5, 2)
#     time.sleep(1)
#     setNeo(green, 5, 0)
#     time.sleep(1)
#     setNeo(purple, 5, 3)
#     time.sleep(1)


# Example usage
#setNeo(c.gr)  # Uses greenC directly (without string lookup)

