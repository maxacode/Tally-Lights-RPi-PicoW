from getConfig import getConf
from json import loads

config  = getConf('baseConfig.json')
print(config.sections())
print('\n')
print(config.items('global')['baseStationName'])

# for section in config.sections():
#     for key in config.options(section):
#         form_key = f"{section}_{key}"  # Composite key for each field in the form
#         #print(formData[form_key])
#         if form_key in formData:
#             #Checking if field is diff from saved field, if is pass if diff update config
#             if config.items(section)[key] == formData[form_key]:
#                 pass
#             else:
#                 print(f'form key DIFF {config.items(section)[key]} {formData[form_key]} ')
#                 config.set(section, key, formData[form_key])
# #     
"""
('tallybase',)
{'tally1': [16, 17], 'tally4': [22, 26], 'tally3': [20, 21], 'tally2': [18, 19]}
[16, 17] 16
                   ---------                       
([16, 17],)
[22, 26] 22
                   ---------                       
([22, 26],)
Traceback (most recent call last):
  File "<stdin>", line 356, in <module>
  File "<stdin>", line 95, in setupMappings
ValueError: invalid pin


Task exception wasn't retrieved
future: <Task> coro= <generator object 'start' at 3c186ac0>
Traceback (most recent call last):
  File "asyncio/core.py", line 1, in run_until_complete
  File "/lib/mdns_client/client.py", line 74, in start
  File "/lib/mdns_client/client.py", line 81, in _init_socket
OSError: [Errno 112] EADDRINUSE



"""