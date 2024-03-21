from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process_data():
    data = request.get_json()  # Get the data from the request
    # Process the data and generate a response
    response = {'message': 'Data received successfully', 'data': data}
    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)