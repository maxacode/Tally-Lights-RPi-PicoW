# Autogenerated file
def render(clients):
    yield """<!DOCTYPE html>
<html>
<head>
    <style>
        table """
    yield """{
            width: 50%;
            border-collapse: collapse;
        }
        th, td """
    yield """{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th """
    yield """{
            background-color: #4CAF50;
            color: white;
        }
    </style>
</head>
<body>

<h2>Clients that are Connected</h2>
<h3><a href=\"/\">Config Editor</a></h3>
<button type=\"button\" onclick=\"sendWifi()\">Send WiFi to all online Tallys</button>
<div id=\"banner-container\"></div>

<table>
    <tr>
        <th>IP Address</th>
        <th>Tally ID #</th>
    </tr>
    """
    for ip, value in clients.items():
        yield """    <tr style=\"background-color: hsl("""
        yield str(value * 20)
        yield """, 100%, 50%);\">
        <td>"""
        yield str(ip)
        yield """</td>
        <td>"""
        yield str(value)
        yield """</td>
    </tr>
    """
    yield """</table>
    <script>
        function sendWifi() """
    yield """{
            // Send JSON HTTP POST request
            fetch('/', """
    yield """{
                method: 'POST',
                headers: """
    yield """{
                    'Content-Type': 'application/json',
                    'Send-Wifi': 'True'
                }
            })
            // Display the banner immediately
            const banner = document.createElement('div');
            banner.classList.add('banner');
            banner.textContent = 'Sending Wifi to Tallys, They will reboot Automatically!';
            document.getElementById('banner-container').appendChild(banner);

            // Hide the banner after a few seconds
            setTimeout(() => """
    yield """{
                banner.remove();
            }, 30000); // Adjust the time as needed
    }
</script>
</body>
</html>
"""