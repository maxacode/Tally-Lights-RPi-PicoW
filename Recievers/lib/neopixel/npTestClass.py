"""
 v1.1 - works 11/20 
 - added docs to each function
 - gets defualt brightness for each color if brighenss not passed in, for non mapped colors it will use default of 50
 #Todo get config and add those to colors mpas
 
"""
from lib.neopixel.neopixel import Neopixel

green = (255, 0, 0)
red = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
off = (0, 0, 0)

# Global dictionary to store brightness levels for each color
color_brightness = {
    red: 100,
    green: 20,
    blue: 30,
    white: 50,
}

class NeoPixelController:
    def __init__(self, brightness_level: int = 50, num_pixels: int = 5, pin: int = 28, pixel_order: str = "RGB") -> None:
        """
        Initialize the NeoPixelController with default brightness and configuration.

        Args:
            brightness_level (int): Default brightness level for NeoPixels (default is 50).
            num_pixels (int): Number of NeoPixels in the strip (default is 5).
            pin (int): Pin number for the NeoPixel data line (default is 28).
            pixel_order (str): Pixel color order (default is "RGB").

        Return: None

        """
        self.strip = Neopixel(num_pixels, 0, pin, pixel_order)
        self.brightness_level = brightness_level
        self.strip.brightness(self.brightness_level)

        # Predefined colors
        self.green = green
        self.red = red
        self.blue = blue
        self.white = white
        self.off = off

    def setNeo(self, color, level=None, pixel_id=0, reset=False) -> tuple[str, int]:
        """
        Set a NeoPixel to a specific color and brightness level.

        Args:
            color (str or tuple): Color name as a string ("red", "green", etc.) or RGB color tuple.
            level (int, optional): Brightness level (overrides the stored brightness for the color). Defaults to None.
            pixel_id (int, optional): Pixel index to set (default is 0).
            reset (bool, optional): Whether to reset all pixels to off before setting (default is False).

        Returns:
            tuple: RGB color tuple, brightness level, pixel index, reset flag.
        """
        if reset:
            self.strip.fill(self.off)

        # Get brightness from color name or global dictionary
        brightness = level if level is not None else color_brightness.get(color)

        if brightness is None:
            # Handle case where color is not found in the dictionary
            print(f"Warning: Color '{color}' not found in brightness dictionary, using default brightness.")
            brightness = self.brightness_level

        self.strip.brightness(brightness)
        self.strip.set_pixel(pixel_id, color)
        self.strip.show()
        return color, pixel_id

if __name__ == '__main__':
    # Create a NeoPixelController instance with a static brightness level of 100
    controller = NeoPixelController(brightness_level=100)
    # Use the controller to set NeoPixel colors
    controller.setNeo("green")  # Uses greenBrightness
    controller.setNeo("red", level=50)  # Uses level 50
    print(controller.setNeo((255, 255, 0)))  # Uses default brightness for white


