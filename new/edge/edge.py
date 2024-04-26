import socket
import requests
# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the host and port
host = '0.0.0.0'
port = 5001

# API endpoint URL
api_url = 'http://192.168.10.243:5003/api'

try:
    # Bind the socket to the host and port
    s.bind((host, port))

    # Listen for incoming connections
    s.listen(1)
    print('Waiting for connection...', flush=True)

    while True:
        # Accept a connection
        conn, addr = s.accept()
        print('Connected by', addr)

        # Receive data and store it in a list
        data_list = []
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data_list.append(data.decode())

        # Close the connection
        conn.close()

        # Add all the values in the list and store it in a variable
        total = sum(map(int, data_list))
        print('Total:', total, flush=True)

        # Send the total to the API endpoint
        response = requests.post(api_url, json={'message': total})
        if response.status_code == 200:
            print('Total sent to API successfully!', flush=True)
        else:
            print('Failed to send total to API:', response.status_code, flush=True)

except Exception as e:
    print('Error:', e, flush=True)

finally:
    # Close the socket
    s.close()
