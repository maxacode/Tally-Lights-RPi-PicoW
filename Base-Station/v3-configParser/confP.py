from configparser import ConfigParser
name = ConfigParser.ConfigParser()
name.read('config.ini')

for section in name.sections():
    print(section)
    for key in name.options(section):
        print(key)
        value = name.items(section)[key]
        form_key = f"{section}_{key}"  # Composite key for each field in the form
        #print(form_key)
        #if form_key in request.form:
          #  config[section][key] = request.form[form_key]
        value = 'AAA'
        name.set(section, key, value)
        
name.write('config.ini')