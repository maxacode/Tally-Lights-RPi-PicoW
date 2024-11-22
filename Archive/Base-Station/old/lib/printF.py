printFOn = True
printFFOn = True
printWOn = True

def printF(*args):
    print("                   ---------                       ")

    if printFOn == True:
        print(args)
            
def printFF(*msg):
    print("                   ---------                       ")
    if printFFOn == True:
        print(msg)
    elif printFOn == True:
        printF(msg)
        
def printW(*msg):
    print("                   ---------                       ")
    if printWOn == True:
        print(msg)
    elif printFon == True:
        printF(msg)