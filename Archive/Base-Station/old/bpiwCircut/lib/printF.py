printFOn = True
printFFOn = True
printWOn = True

def printF(*args):
    if printFOn == True:
        print(args)
            
def printFF(*msg):
    if printFFOn == True:
        print(msg)
    elif printFOn == True:
        printF(msg)
        
def printW(*msg):
    if printWOn == True:
        print(msg)
    elif printFOn == True:
        printF(msg)
        