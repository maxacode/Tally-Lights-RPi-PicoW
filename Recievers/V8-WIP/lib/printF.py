printFOn = True
printFFOn = True
printWOn = True
from time import time,sleep

timeStart = time()

def printF(*msg):
    if printFOn == True:
        print(f'{time() - timeStart}, {msg}')
            
def printFF(*msg):
    if printFFOn == True:
        print(f'{time() - timeStart}, {msg}')
    elif printFOn == True:
        printF(msg)
        
def printW(*msg):
    if printWOn == True:
        print(f'{time() - timeStart}, {msg}')
    elif printFOn == True:
        printF(msg)

