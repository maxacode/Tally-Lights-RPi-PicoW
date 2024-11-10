# Autogenerated file
def render(name):
    yield """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Configuration Editor</title>
    <style>
    /* Center the form element */
    form """
    yield """{
      position: absolute;
      top: 55%;
      left: 30%;
      transform: translate(-50%, -50%); 
    }
    </style>
</head>
<body>
    <form id=\"configForm\">
    <h1>Edit Configuration</h1>
    <button type=\"button\" onclick=\"submitConfig()\">Save Changes</button>
    """
    for section in name.sections():
        yield """        """
        if name.items(section)['title'] != "hidden":
            yield """            <h2> """
            yield str(section)
            yield """ : """
            yield str(name.items(section)['title'])
            yield """</h2>
            """
            for key in name.options(section):
                yield """                """
                if key != "title":
                    yield """                    <label for=\" """
                    yield str(section)
                    yield """_"""
                    yield str(key)
                    yield """\">"""
                    yield str(key)
                    yield """:</label>
                    <input type=\"text\" id=\""""
                    yield str(section)
                    yield """_"""
                    yield str(key)
                    yield """\" name=\""""
                    yield str(section)
                    yield """_"""
                    yield str(key)
                    yield """\" value=\""""
                    yield str(name.items(section)[key])
                    yield """\" size = \"30\" >
                    <br><br>
                """
                yield """             """
            yield """     
        """
        yield """    """
    yield """    </form>

    <script>
        function submitConfig() """
    yield """{
            const form = document.getElementById('configForm');
            const formData = """
    yield """{};

            // Gather form data
            Array.from(form.elements).forEach(element => """
    yield """{
                if (element.name) """
    yield """{
                    formData[element.name] = element.value;
                }
            });

            // Send JSON HTTP POST request
            fetch('/', """
    yield """{
                method: 'POST',
                headers: """
    yield """{
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => """
    yield """{
                console.log('Success:', data);
            })
            .catch((error) => """
    yield """{
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>


"""
