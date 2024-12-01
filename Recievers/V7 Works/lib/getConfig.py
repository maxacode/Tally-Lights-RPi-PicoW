#Gets config and returns
# # V3.3 - VSCode

from configparser import ConfigParser

def getConf(configFileName) -> ConfigParser:
    """
    Get config file by name and returns the ConfigParser object

    Params:
        configFileName (str): Name of the config file

    Returns:
        ConfigParser: ConfigParser object

    """

    config = ConfigParser.ConfigParser() # type: ignore
    config.read(configFileName)
    return config
    
if __name__ == '__main__':
    getConf('baseConfig.json')