# Autogenerated file
def render(name):
    yield """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <title>Update Config</title>
</head>
<body>
    <h1>Update Configuration</h1>
    <button type=\"submit\">Save Changes</button>
    <form method=\"POST\">
        """
    for section in name.sections():
        yield """            <h2>"""
        yield str(section)
        yield """</h2>
            """
        for key in name.options(section):
            yield """                <label for=\""""
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
            yield """\" size = \"60\" >
                <br><br>
            """
        yield """        """
    yield """       
    </form>
</body>
</html>"""
