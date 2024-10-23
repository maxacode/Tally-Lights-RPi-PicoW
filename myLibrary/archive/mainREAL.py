from machine import Pin, PWM
from time import sleep
#import urequests as requests
import requests



#import connectToWlan
#connectToWlan.connectWLAN()
import myLibrary.apMode as apMode
apMode.ap_mode()
print(apMode.ap.isconnected())
print(apMode.ap.ifconfig())

# make a urequest to 192.168.88.232/led16on then off

request_url = 'http://192.168.88.234/'
off = "led16off"
on = "led16on"


#while True:

    # response = requests.get(request_url+on)
    # # Print results
    # print('Response code: ', response.status_code)
    # print('Response text:', response.text)
    # sleep(2)
    # response = requests.get(request_url+off)
    # print('Response code: ', response.status_code)
    # print('Response text:', response.text)
    # sleep(1)