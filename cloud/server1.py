import socket
import logging
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024)
        if not request:
            break
        logger.info(f"Received: {request}")  # Log received data
    client_socket.close()

def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5001))
    server.listen(5)
    logger.info("Listening on 0.0.0.0:5001")  # Log server startup

    while True:
        client, addr = server.accept()
        logger.info(f"Accepted connection from: {addr[0]}:{addr[1]}")  # Log accepted connection
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
