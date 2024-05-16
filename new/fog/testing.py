from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

def process_data(data):
    # Perform computation on the received data
    # This function can take some time to execute
    # For example, let's assume we are just printing the data
    print("Processing data:", data)

@app.route('/api', methods=['POST'])
def receive_data():
    # Receive data over API
    data = request.get_json()
    
    # Send acknowledgment response
    response_data = {'message': 'Data received'}
    threading.Thread(target=process_data, args=(data,)).start()
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
