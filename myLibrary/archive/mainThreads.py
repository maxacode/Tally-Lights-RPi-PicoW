import time, socket, network

apMode = False

if apMode == True:
    import myLibrary.archive.apWorks as apWorks
    apWorks.setup_ap()
elif apMode == False:
    import Recievers.connectToWlan as connectToWlan
    connectToWlan.connectWLAN()

print("vtempMain: 1.1")


# # Dictionary to store clients' IP addresses with numerical order
# clients = {}
# client_id = 1  # Numerical order starts at 1
# server_socket_port = 8080

# # Function to handle incoming socket connections
# def accept_connections():
#     global client_id, server_socket_port
#     # Create a TCP/IP socket
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # Bind the socket to the local address and a specific port
#     server_socket.bind(('0.0.0.0', server_socket_port))
#     # Listen for incoming connections (queue up to 5)
#     server_socket.listen(10)
    
#     print(f"Server listening on port {server_socket_port}...")
    
#     while True:
#         try:
#             # Accept a new client connection
#             client_socket, client_addr = server_socket.accept()
#             client_ip = client_addr[0]
            
#             # Add the client to the dictionary
#             clients[client_id] = client_ip
#             print(f"Client {client_id} connected with IP: {client_ip}")
#             client_id += 1
#             print(clients)
            
         
#         except Exception as e:
#             print("Error accepting connection:", e)
#             break
    
#     # Close the server socket if we exit the loop
#     server_socket.close()


# # Function to remove client from the dictionary on disconnection
# def remove_client(client_ip):
#     for key, value in list(clients.items()):
#         if value == client_ip:
#             del clients[key]
#             print(f"Client {key} with IP {client_ip} has disconnected.")
#             break

# # Start accepting socket connections
# accept_connections()


import socket
import _thread
import time

# Server settings
host = '0.0.0.0'  # Listen on all interfaces
port = 8080       # Port to listen on

# Keep-alive timeout (in seconds)
keep_alive_timeout = 5

# Dictionary to store client connections and last keep-alive times
clients = {}

# Function to handle each client
def handle_client(client_socket, client_address):
    print(f"New connection from {client_address}")
    clients[client_address] = time.time()  # Store the connection time for keep-alive checks

    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                break  # Client disconnected
            
            data = data.strip()
            if data == b"keep-alive":
                # Update the client's last keep-alive time
                clients[client_address] = time.time()
                print(f"Keep-alive received from {client_address}")
            else:
                # Process the received command
                print(f"Command received from {client_address}: {data.decode()}")
                response = process_command(data)
                client_socket.send(response)
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        print(f"Client {client_address} disconnected")
        del clients[client_address]
        client_socket.close()

# Function to process commands from the client
def process_command(command):
    if command == b"ping":
        return b"pong"
    elif command == b"turn_led_on":
        # Here you could trigger an actual device if needed
        return b"LED is ON"
    elif command == b"turn_led_off":
        # Here you could trigger an actual device if needed
        return b"LED is OFF"
    else:
        return b"Unknown command"

# Function to listen for new client connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server is listening on {host}:{port}")

    while True:
        # Accept new client connection
        client_socket, client_address = server_socket.accept()
        # Start a new thread to handle the client
        client_thread = _thread.start_new_thread(handle_client, (client_socket, client_address))


# Function to check for keep-alive timeouts
def keep_alive_monitor():
    while True:
        time.sleep(5)  # Check every 5 seconds
        current_time = time.time()
        disconnected_clients = []
        for client_address, last_keep_alive in clients.items():
            if current_time - last_keep_alive > keep_alive_timeout:
                print(f"Client {client_address} timed out (no keep-alive received).")
                disconnected_clients.append(client_address)
        
        # Clean up disconnected clients
        for client_address in disconnected_clients:
            del clients[client_address]

# Start the server and keep-alive monitor in separate threads
if __name__ == "__main__":
    # Start the server thread
    server_thread = _thread.start_new_thread(start_server())

    server_thread.start()

    # Start the keep-alive monitor thread
    monitor_thread = _thread.start_new_thread(keep_alive_monitor)
    monitor_thread.start()
