# https://docs.circuitpython.org/projects/asyncio/en/latest/examples.html

from lib.npDone import setNeo
from time import sleep
 
import asyncio



async def loopNeo():
    for x in range(0, 5):
        for y in range(0, 255, 30):
            setNeo((y,0,x + 60), .5, x, True)
            await asyncio.sleep(.3)


async def mainFunc():
    
    x = 1
    while True:
        print(x)
        x+=1
        await asyncio.sleep(1)
    

    
asyncio.create_task(mainFunc())
asyncio.run(loopNeo())
