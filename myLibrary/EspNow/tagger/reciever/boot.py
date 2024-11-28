from time import sleep

from testPWM import setPWM as vib


for _ in range(8, 11):
    vib(_)
    sleep(.7)
    vib(0)
    sleep(.3)


#import reciever.py
