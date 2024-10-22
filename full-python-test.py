print("hello world")
import socket,time

baseIP = '192.168.88.231'
basePort = 8080

# Keep-alive interval (in seconds)
keep_alive_interval = 10      

# Function to connect to the server
def connect_to_server():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the server
        client_socket.connect((baseIP, basePort))
        print("Connected to server:", baseIP, basePort)
    except Exception as e:
        print("Failed to connect:", e)
        return None
    return client_socket

# Function to handle commands from the server
def handle_command(command):
    print("Received command:", command.decode())  # Decode and display the command
    # Implement command handling logic here
    if command == b"ping":
        return b"pong"
    elif command == b"turn_led_on":
        # Add code to turn on an LED (example: using GPIO pin control)
        return b"LED is ON"
    elif command == b"turn_led_off":
        # Add code to turn off an LED
        return b"LED is OFF"
    else:
        return b"Unknown command"
# Function to keep connection alive and listen for commands
def run_client():
    client_socket = connect_to_server()
    if not client_socket:
        return  # Exit if connection failed

    last_keep_alive = time.time()  # Track time for sending keep-alive
    try:
        while True:
            # Check if it's time to send a keep-alive message
            if time.time() - last_keep_alive > keep_alive_interval:
                try:
                    client_socket.send(b"keep-alive")  # Send keep-alive message
                    print("Keep-alive sent.")
                    last_keep_alive = time.time()  # Reset the keep-alive timer
                except Exception as e:
                    print("Error sending keep-alive:", e)
                    break

            # Check if there is incoming data from the server
            try:
                client_socket.settimeout(1)  # Set timeout for non-blocking behavior
                command = client_socket.recv(1024)  # Wait for a command
                if command:
                    response = handle_command(command)  # Process the command
                    client_socket.send(response)  # Send response to server
            except socket.timeout:
                # No data received, continue the loop (non-blocking)
                continue
            except Exception as e:
                print("Error receiving data:", e)
                break
    finally:
        print("Closing connection.")
        client_socket.close()

# Start the client
run_client()