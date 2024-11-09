from gc import mem_free
print(mem_free())
from getConfig import getConfig
from connectToWlan import mainFunc


config = getConfig('baseConfig.json')
mainFunc(config,True)
