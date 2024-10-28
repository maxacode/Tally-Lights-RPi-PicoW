

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

import json
with open('baseConfig.json', 'r') as f:
    config = json.dump(f)
    print(config)

print("$#####################")
for x in config.keys():
    print(x, config[x])