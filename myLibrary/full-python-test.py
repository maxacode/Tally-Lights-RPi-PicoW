# Testing python stuff NOT MICRO PYTHON

# 
# POST requestprint("hello world")
# import socket,time,requests,json

#  ########### recvSetup #################
# # Sending a post to base and recvSetup with IP and Tally ID
# ip = '192.168.88.231'
# tallyID = '01'
# url = 'http://192.168.88.234:8080/recvSetup'
# #url = base + '?ip=' + ip + '&tallyID=' + tallyID
# myIP = socket.gethostbyname(socket.gethostname())
# print(myIP)
# data = {'key1': 'value1', 'key2': 'value2'}
# headers = {'Content-Type': 'application/json','ip':ip, 'tallyID':tallyID}

# response = requests.post(url, data=json.dumps(data),
#  headers=headers,timeout = 2)

# if response.status_code == 200:
#     print('Request successful')
#     print(response)
# else:
#     print('Request failed')


# Given a string of 8 numbers, split it into 4 lists of 2 numbers each
number_string = "12345678"

# Split the string into chunks of 2 and store them in a list of lists
result = [list(number_string[i:i+2]) for i in range(0, len(number_string), 2)]
print(result)
