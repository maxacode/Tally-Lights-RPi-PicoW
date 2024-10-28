

# import socket,time,requests,json

#  ########### recvSetup #################
# # Sending a post to base and recvSetup with IP and Tally ID
# ip = '192.168.88.231'
# tallyID = '01'
# url = 'http://tally.local:8080/recvSetup'
# #url = base + '?ip=' + ip + '&tallyID=' + tallyID
# #myIP = socket.gethostbyname(socket.gethostname())
# #print(myIP)
# #data = {'key1': 'value1', 'key2': 'value2'}
# while True:

#     try:
#         x = 0
#         y = 1
#         headers = {'ip':'192.168.88.247', 'tallyID':str(4)}

#         response = requests.post(url,
#         headers=headers,timeout = 2)
#         print(response.text)
#         if response.status_code == 200:
#             print('Request successful')
#             print(response)
#         else:
#             print('Request failed')

#         x = 1 
#         y = 0
#         time.sleep(.5)
#         headers = {'Content-Type': 'application/json', 'ledStatus':f'{x}{y}000000'}

#         response = requests.post(url,
#         headers=headers,timeout = 2)
#         print(response.text)

#         if response.status_code == 200:
#             print('Request successful')
#             print(response)
#         else:
#             print('Request failed')
#         time.sleep(.5)
#     except Exception as e:
#         print(e)

#     # import json

#     # updateThis = {'version': '1.11'}

#     # with open('baseConfig.json', 'r') as f:
#     #     config = json.load(f)
#     #     print(config)

#     # config['global']['version'] = '1.9'

#     # with open('baseConfig.json', 'w') as f:
#     #     json.dump(config, f)

# import json
# with open('baseConfig.json', 'r') as f:
#     config = json.dump(f)
#     print(config)

# print("$#####################")
# for x in config.keys():
#     print(x, config[x])
import json
with open('baseConfig2.json', 'r') as f:
    config = json.load(f)


tal = (config["tally1"])
res = json.loads(tal)

print(res)
print(type(res))
print(res[0])
print(json.loads(config['tally1'])[0    ])
#for x in config:
  #  print(x)
#for x in dict(config['global']):
  #  print(x)

config2 = {"tallyBrightness": {"tally1": 111, "tally4": 222, "tally3": 333, "tally2": 40000}, "tallyLEDStatus": {"tally1": [12, 35000], "tally4": [15, 35000], "tally3": [14, 35000], "tally2": [13, 35000]}, "gpioInput": {"tally1": [17, 16], "tally4": [26, 22], "tally3": [21, 20], "tally2": [19, 18]}, "tallyEnabled": {"tally1": "True", "tally4": "True", "tally3": "True", "tally2": "True"}, "api": {"ledControlEndpoint": "led", "receiverSetup": "recvSetup"}, "global": {"apMode": "False", "apSSID": "TallySystemSSID", "apPassword": "KakDela!", "wlanSSID": ["Tell My Wi-Fi Love Her", "OC-Staff"], "baseStationName": "tally2", "wlanPassword": ["GodIsGood!", "loveGodloveothers"], "version": 88}, "_comments/sections": {"tallyBrightness": "Tally LED brightness 0 - 65000", "tallyLEDStatus": "Tally LED GPIO pins that show Connection status and brightness ", "gpioInput": "GPIO pins that are used for input buttons for now", "tallyEnabled": "Tally LED enabled or disabled", "title": "Base station configuration", "global": "Global configuration", "api": "API configuration"}}


config.update(config2)

#print(config["global"]["version"])
#print(config['tallyLEDStatus']['tally1'][0])