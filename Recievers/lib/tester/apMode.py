

import network
import time
print("v2.3")

# Function to configure the ESP in AP mode
def setup_ap(ssid, password):
    # Create a WLAN object for AP mode
    ap = network.WLAN(network.AP_IF)

    
    # Configure AP settings
    ap.config(essid=ssid, password=password)  # Set SSID and password

    # Create a WLAN object for AP mode
    ap = network.WLAN(network.AP_IF)


    # Activate AP mode
    ap.active(True)
    
    # Wait until AP is active
    while not ap.active():
        time.sleep(1)
    
    # Display AP's IP configuration
    print("Access Point active with IP:", ap.ifconfig())

# Function to monitor client connections
def monitor_client_connections(ap):
    previous_clients = set()
    
    while True:
        # Get a list of connected stations (clients)
        clients = ap.status('stations')
        current_clients = set([client[0] for client in clients])

        # Check for new clients
        new_clients = current_clients - previous_clients
        if new_clients:
            for client in new_clients:
                print("New client connected with MAC address:", client)
        
        # Update the previous clients list
        previous_clients = current_clients

        # Wait a bit before checking again
        time.sleep(5)

# SSID and password for the Access Point
ssid = "ESP_AP"
password = "12345678"

# Set up the ESP in AP mode
setup_ap(ssid, password)


# Monitor client connections
#monitor_client_connections(ap)
