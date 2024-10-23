#https://electrocredible.com/neopixel-micropython-raspberry-pi-pico-ws2812b/
import neopixel, machine
np = neopixel.NeoPixel(machine.Pin(15), 6)
np[0] = (255,0,0)
np[1] = (0,255,0)
np[2] = (0,0,255)
np[3] = (255,255,0)
np[4] = (255,0,255)
np[5] = (255,255,255)
np[6] = (0,255,255)
