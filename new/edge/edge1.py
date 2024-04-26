import socket

# Define the host and port
host = '0.0.0.0'  # Listen on all available network interfaces
port = 5000

try:
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    s.bind((host, port))

    # Listen for incoming connections
    s.listen(1)
    print(f"Server listening on port {port}...", flush=True)

    while True:
        # Accept a connection
        conn, addr = s.accept()
        print(f"Connection established from {addr}")

        # Receive data from the client
        data = conn.recv(1024).decode()
        print(f"Received data: {data}",flush=True)

        # Close the connection
        conn.close()

except Exception as e:
    print('Error:', e)

finally:
    # Close the socket
    s.close()
