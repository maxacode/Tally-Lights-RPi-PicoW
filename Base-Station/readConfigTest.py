import json

def read_config(filename):
  with open(filename, 'r') as f:
    config = json.load(f)
  return config

config = read_config('config.json')

led_pin = config['settings']['led_pin']
button_pin = config['settings']['button_pin']
interval = config['settings']['interval']
greeting = config['messages']['greeting']
goodbye = config['messages']['goodbye']

print(f"LED pin: {led_pin}")
print(f"Button pin: {button_pin}")
print(f"Interval: {interval}")
print(f"Greeting: {greeting}")
print(f"Goodbye: {goodbye}")