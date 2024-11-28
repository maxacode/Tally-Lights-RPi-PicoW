from npDone import setNeo, red, green, blue, white, off
from machine import deepsleep, Pin
import esp32


setNeo(white)

butt1 = Pin(12, Pin.IN)# Pin.PULL_UP)  # pin 43
butt1.off()
#esp32.wake_on_ulp(False)
#esp32.gpio_deep_sleep_hold(False)
esp32.wake_on_ext0(pin = butt1, level = esp32.WAKEUP_ANY_HIGH)
#esp32.wake_on_ext0(pin = butt1, level = esp32.WAKEUP_ALL_LOW) # This works if butt1 is connected to HIGH at all times. 
setNeo(red)
deepsleep()
