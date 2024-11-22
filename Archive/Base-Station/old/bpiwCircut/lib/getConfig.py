#Gets config and returns
from configparser import ConfigParser


def getConfig(configFileName):
    config = ConfigParser.ConfigParser()
    config.read(configFileName)
   # print(config.items('gpioInput'))

    return config
    
if __name__ == '__main__':
    getConfig('baseConfig.json')