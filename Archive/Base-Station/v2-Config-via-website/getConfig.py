#Gets config and returns
import json
configFileName = 'baseConfig.json'
def getConf():
    with open(configFileName,'r') as f:
        config = json.load(f)
        #print(config)
        print('getConfig.py - Global Version: ',config["global"]["version"])
        return config
    
    
if __name__ == '__main__':
    getConf()
    