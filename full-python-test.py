print("hello world")
import requests

res = requests.get('http://192.168.88.234/led16on')
print(res.content)