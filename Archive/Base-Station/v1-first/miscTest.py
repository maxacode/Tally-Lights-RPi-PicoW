import json
filename = 'baseConfig.json'

def read_config():
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

config = read_config()
#print(config)

# check if tallyEnabled is true for each tally thenb add to a list
tallyEnabled = []
current_button_map = []

tallyEnabled = (list(config['tallyEnabled'].values()))
y = 1
gpioInput = config['gpioInput']
print('gpioinput',gpioInput)
for x in tallyEnabled:
    if x:
        
        current_button_map.append(gpioInput['tally'+str(y)])
    elif x == False:
        current_button_map.append([0,0])
    y += 1
print('current map',current_button_map)
current_button_state = ''
for x in current_button_map:
    print('x',x)
    for y in x:
        print('y',y)
        if y == 0:
            current_button_state += '9'
        else:
            current_button_state += '1'

print('current_button_state',current_button_state)