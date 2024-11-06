import gc, os

# Initial memory
print("Initial Free Memory:", gc.mem_free())

from lib.getConfig import getConf
curDir = str(os.listdir())
if "recvConfig" in curDir:
    baseStation = False
    configFileName = 'recvConfig.json'
elif "baseConfig" in curDir:
    baseStation = True
    configFileName = 'baseConfig.json'

config = getConf(configFileName)

print("Memory after config create:", gc.mem_free())#  151776 155248 151776


# Delete variable and collect garbage
del config
gc.collect()
print("Memory after deletion:", gc.mem_free())
gc.collect()
print("Memory after collect:", gc.mem_free())
