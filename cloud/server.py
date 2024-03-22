import socket
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024)
        if not request:
            break
        print(f"Received: {request}")
    client_socket.close()

def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5001))
    server.listen(5)
    print("Listening on 0.0.0.0:5001")

    while True:
        client, addr = server.accept()
        print(f"Accepted connection from: {addr[0]}:{addr[1]}")
        client_handler = Thread(target=handle_client, args=(client,))
        client_handler.start()

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    if 'message' in data and data['message'] == 'hello':
        return jsonify({'reply': 'hello world'})
    else:
        return jsonify({'error': 'Invalid message'}), 400

if __name__ == '__main__':
    Thread(target=start_socket_server).start()
    app.run(host='0.0.0.0', port=5000)