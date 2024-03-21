from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process_data():
    data = request.get_json()  # Get the data from the request

    response_from_cloud = send_api_request_cloud('http://192.168.10.145:5000/api', "edge")

    print(response_from_cloud)

    # Process the data and generate a response
    response = {'message': 'Data received successfully', 'data': data}
    return jsonify(response)

def send_api_request_cloud(url, data):
        response = requests.post(url, json=data)
        return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)