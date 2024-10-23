from machine import Pin 
from time import sleep
z = 0 
current_button_state = []
t1PST = Pin(16, Pin.IN, Pin.PULL_DOWN)
t1PGM = Pin(17, Pin.IN, Pin.PULL_DOWN)
t2PST = Pin(18, Pin.IN, Pin.PULL_DOWN)
t2PGM = Pin(19, Pin.IN, Pin.PULL_DOWN)


while z <= 30: 
    z += 1
    #print(z)
    new_state = []

    allTallys = (t1PST,t1PGM,t2PST,t2PGM)
    for x in allTallys:
        #print(x.value())
        new_state.append(x.value())

    #print(new_state, current_button_state)
    sleep(.5)
    if new_state != current_button_state:
        current_button_state = new_state

        print("Button Changed to:", new_state)
