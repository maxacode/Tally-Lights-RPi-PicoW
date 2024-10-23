
# Dip Label
- https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1r_0sFT2r2zNmSSzLbNwyI4Zi28AwH6iYGQ&s
- https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQfat9j9AMm2MAdwHRRU1NjhUMpF7Lkx7su2A&s
- https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRRvfyZUEwQkg3G_xbB9vQwlyztlVLPx88eQ&s
- https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTTTIc4SweqdtZZ4lm0K69-HV7DHMZbc9rVRSWki5vMNgJifOdwEgnCBr82juwtb5MQNZA&usqp=CAU
- https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJOkgfU0N_XKrlu8SS8g90wMO1g_43NcLfWKxxV0EWtVA1QqJi3D2hAXQmUV20CX49aUE&usqp=CAU
- 
- - Import 
	- network to enable AP MODE
	- time
	- requests
	- Sockets
- setup AP
	- Read AP details from config file 
 
- API
    - baseAPI:
      - Clients registier with their IP and Identifier (1-4)
  	- Tally Input:
    	- one thread that takes input from video switch aka GPIO then adds to que. 
    	- Input: GPIO 1 High = Camera 1 Preview Mode
    	- Que: recv1, preview
	- sendTally
    	- another thread that reads from the queue and makes POST to Recivers waits for confirmation before removing from que
    	- post to http://recv1(IP)/preview
      	- https://medium.com/@desjoerdhaan/quick-and-dirty-iot-prototype-in-10-minutes-be74378f4ded
      	- 