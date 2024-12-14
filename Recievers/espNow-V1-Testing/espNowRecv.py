"""
v1.1 reciever

v1.1 recieves espNow msg, if TU as key then reads vlaues
- parses out only 2 chars that are in tallyID
- enables/disables LED if 1/0
- removed all wr/p since flash was maxed out

"""
tu = "tu" #tu = tally update list of latest pin statess


from machine import Pin
import espnow
import time, asyncio
import network
from json import loads

#Mine
from onBLed import lon, loff, tester, ltog
#test LEDS
loff()
#tester()
from SwriterClass import writeFile
writeFile  = writeFile("recieverLog.txt")
wf = writeFile.wf
wfp = writeFile.wfp

#ESP NOW setup
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()                # Disconnect from last connected WiFi SSID
e = espnow.ESPNow()                  # Enable ESP-NOW
e.active(True)

tallyIDInt = 1
def evalMsg(msgJ: dict) -> None:
    if tu in msgJ.keys():
        #print(msgJ[tu])
                
        source = msgJ[tu]
        output = []

        while source:
            output.append(source[:2])
            source = source[2:]
        
        # Only this tallys LED values
        thisTallyLed = output[tallyIDInt-1]
        if '1' in thisTallyLed[0] or '1' in thisTallyLed[1]:
           # print(thisTallyLed)
            lon()
        elif '0' in thisTallyLed[0] or '0' in thisTallyLed[1]:
            #print(thisTallyLed)
            loff()
             



                    
def rx():
    #wf(f'ESPNOW rx-start ')
    try:
        while True:
            host, msg = e.recv()
            if msg:
                # load data fro JSON
               # print(msg)
                #print(loads(msg)['tagger'])

                try:
                    msgD = msg.decode()
                    msgJ = loads(msgD)
                    #print(msgJ)
                except Exception as Error:
                    msgJ = msg
                  #  wf(f'ERORR: msgJ not JSON : {Error}')
                #finally:
                   # wfp(f'INFO MSG Recieved: {e.peers_table=}  :  {msgJ=}')
                
                evalMsg(msgJ)
                    
    except Exception as Error:
        print(Error)
                
rx()