import time, socket, network
print("vtempMain: 1.5")
from microdot import Microdot
import Recievers.connectToWlan as connectToWlan
from time import sleep
from machine import Pin
####### setup AP ######################

apMode = False

if apMode == True:
    import myLibrary.apWorks as apWorks
    apWorks.setup_ap()
elif apMode == False:
    connectToWlan.connectWLAN()

####################################
 

 ####### API ######################
app = Microdot()
clients = {}

 

 ########### baseAPI #################
@app.post('/recvSetup')
async def createClient(request):
    #print("requests.json: ", request.json())
    #print("requests.body: ", request.body)
    #requests.body:  b'----------------------------259069186789993276085327\r\nContent-Disposition: form-data; name="hello"\r\n\r\nworld\r\n----------------------------259069186789993276085327\r\nContent-Disposition: form-data; name="privet"\r\n\r\njoe\r\n----------------------------259069186789993276085327--\r\n'
    #print("requests.headers: ", request.headers)
    #requests.headers:  {'User-Agent': 'PostmanRuntime/7.42.0', 'Postman-Token': 'f2650444-0d94-43e8-98d4-5388fd274000', 'Content-Type': 'multipart/form-data; boundary=--------------------------259069186789993276085327', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive', 'Host': '192.168.88.231:8080', 'Accept': '*/*', 'Content-Length': '273'}
    print("requests.headers.ip: ", request.headers['ip'])
    print("requests.headers.tallyID: ", request.headers['tallyID'])
    print("requests.url: ", request.url)
    #requests.url:  /recvSetup?test123=hello123
    print("requests.json: ", request.json)
    print("requests.form: ", request.form)

    # add client it 
    clients[request.headers['tallyID']] = request.headers['ip'] 
    print(clients)

    return "ack", 200, {'Content-Type': 'text/html'}



@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

app.run(debug=True)
