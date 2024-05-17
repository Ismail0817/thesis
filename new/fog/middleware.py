import json
import subprocess
import threading
from flask import Flask, request
import requests
import yaml
from kubernetes import client, config


app = Flask(__name__)

@app.route('/api', methods=['POST'])
def handle_api_request():
    request_data = request.get_json()
    global task_type
    
    # Extract the request type from the request data
    # task_type = request_data.get('task')
    
    message_json = request_data['message']
    task = request_data['task']

    # Parse the JSON string in the message
    message = json.loads(message_json)

    # Now `message` is a list of dictionaries and `task` is a string
    # print("Message:", message)
    print("Task:", task)

    # print(request_data)
    # print(type(request_data))
    # print(request_data.get('message'))

    if task == 'task2' or task == 'task3':
        # Perform task 2
        result = negotiate_fog()
        print(result)   
        if result == "success":
            threading.Thread(target=perform_task2, args=(message,)).start()
            return {'result': 'Task 2 deployed successfully wait for result'}
        else:
            return {'result': 'Task 2 failed because of fog negotiation failure'}
    else:
        # Invalid request type
        return {'error': 'Invalid request type'}

    # return {'result': 'data received in fog middleware API'}

def perform_task2(message):
    # Logic for task 2
    # ...
    print("inside thread\n sending data to fog container\n")
    # print("Message:", message)
    # Send data to the API endpoint
    response = requests.post("http://192.168.10.243:5005/preprocess", json=message)
    print(response.text)
    payload = {'message': response.text, 'task': 'task2'}
    response = requests.post('http://192.168.10.243:5003/api', json=payload)

    # Print the response from the server
    print(response.json())
    # print(request_data.get('message'))
    

def negotiate_fog():
    script_path = "/root/thesis/new/edge/bash.sh" 
    script_output = run_shell_script(script_path)
    
    # Split the string into lines
    lines = script_output.strip().split('\n')

    # Extract headers
    headers = lines[0].split()

    # Initialize dictionaries to store data for each node
    node_data = {}

    # Process data for each line
    for line in lines[1:]:
        # Split line into fields
        fields = line.split()
        node_name = fields[0]
        node_values = {
            headers[i]: fields[i] for i in range(1, len(headers))
        }
        node_data[node_name] = node_values
    
    negotiation = "unsuccess"
    for node_name, values in node_data.items():
        if int(values['CPU%'].rstrip('%')) < 50 and int(values['MEMORY%'].rstrip('%')) < 50:
            print(f"Node: {node_name} -> CPU usage is {values['CPU%']} and memory usage is {values['MEMORY%']}")
            negotiation = "success"
        else:
            print(f"Node: {node_name} -> CPU usage is {values['CPU%']} and memory usage is {values['MEMORY%']}")

    # # negotiation with fog
    # response_from_fog = send_api_request_fog('http://192.168.10.147:5000/api', "negotiate")
    # print(response_from_fog)
    # return jsonify({'reply': negotiation, 'data': node_data})
    return negotiation

def run_shell_script(script_path):
    try:
        # Run the shell script using subprocess and capture output
        completed_process = subprocess.run(['bash', script_path], capture_output=True, text=True, check=True)
        # Access the captured output from completed_process.stdout
        script_output = completed_process.stdout
        # Return the captured output
        return script_output
    except subprocess.CalledProcessError as e:
        print(f"Error running shell script: {e}")
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)