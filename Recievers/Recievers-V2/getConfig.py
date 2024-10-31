#Gets config and returns
from configparser import ConfigParser
config = ConfigParser.ConfigParser()


def getConf(configFileName):
    

    config.read(configFileName)
    configDict = {}
    return config
    
if __name__ == '__main__':
    getConf()
    
#config.write('baseConfig.json')