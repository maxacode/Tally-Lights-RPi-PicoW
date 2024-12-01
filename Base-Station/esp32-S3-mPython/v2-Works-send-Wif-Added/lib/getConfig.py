#Gets config and returns
from configparser import ConfigParser


def getConf(configFileName):
    config = ConfigParser.ConfigParser()
    config.read(configFileName)
    return config
    
if __name__ == '__main__':
    getConf('baseConfig.json')