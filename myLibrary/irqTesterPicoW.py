""" Tsend test via gpio:

tally3 = [5,6]
tally2 = [3,4]
tally4 = [7,8]
tally1 = [1,2]

Run file and push button to run test()


"""
from machine import Pin
from time import sleep
from random import randint

# PM  = Primary PR preview
t1PM = Pin(16, Pin.OUT, Pin.PULL_DOWN)
t1PR = Pin(17, Pin.OUT, Pin.PULL_DOWN) # 

t2PM = Pin(18, Pin.OUT, Pin.PULL_DOWN)
t2PR = Pin(19, Pin.OUT, Pin.PULL_DOWN)

t3PM = Pin(20, Pin.OUT, Pin.PULL_DOWN)
t3PR = Pin(21, Pin.OUT, Pin.PULL_DOWN)

t4PM = Pin(22, Pin.OUT, Pin.PULL_DOWN)
t4PR = Pin(26, Pin.OUT, Pin.PULL_DOWN)

allPins = [t1PM, t1PR, t2PM, t2PR, t3PM,t3PR,t4PM,t4PR]

for pin in allPins:
    pin.off()
    
def runTest(interuptPin):
    if interuptPin.value() == 0:
        #allPins = [t1PM, t1PR]
#         runCut()

        print("\n\nrunning all .6 sleep total")
        for pin in allPins:
            pin.on()
           # print(pin.value(), end=' | ' )
            sleep(.35)
            pin.off()
            #print(pin.value(), end=' | ' )
            sleep(.35)
            
        print('about to runCut')
        runCut()

def runCut():
    # Simulate a cut
    # t1 Pm on and t2 Pr on
    print('runCut ')
    t1PM.on()
   # sleep(.4)
    t2PR.on()
    sleep(.5)
    
    print('off')
    t1PM.off()
    #sleep(.2)
    t2PR.off()
    sleep(.3)
    
    
    
    print('on')
    t1PR.on()
    t2PM.on()
    sleep(.5)
    
    print('off')
    t2PM.off()
    t1PR.off()
    sleep(.3)
#     
    
    
    
but1 = Pin(12, Pin.IN, Pin.PULL_UP) # 1 is not PRessed, 0 is pressed
#but1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=runTest)
but1.irq(trigger=Pin.IRQ_FALLING, handler=runTest)

