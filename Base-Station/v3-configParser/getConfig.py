#Gets config and returns
from configparser import ConfigParser
config = ConfigParser.ConfigParser()


def getConf(configFileName):
    

    config.read(configFileName)
    configDict = {}
    tallyEnabled = tallyID2 = config.items('tallyLEDStatus')['tally1'].split(',')[0]
    
    #print(tallyEnabled)
    
    #for x in name.sections():
        #print(x)
        #for y in name.options(x):
           # print(y)
           #print(name.items(x)[y])
           # configDict[x] = 
       # configDict[x] = name.options(x)
        #print(configDict)
    #config_dict = {section: dict(name.sections()) for section in name.options(section)}
   # print(config_dict)
    return config
    
if __name__ == '__main__':
    getConf()
    