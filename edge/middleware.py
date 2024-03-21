from flask import Flask, request, jsonify
import requests
import yaml
from kubernetes import client, config
import subprocess

app = Flask(__name__)

# Load kubeconfig file to authenticate with the Kubernetes cluster
config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

# Create Kubernetes API client
apps_v1 = client.AppsV1Api()

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



@app.route('/api', methods=['POST'])
def process_data():
    data = request.get_json()  # Get the data from the request

    # response_from_fog = send_api_request_fog('http://192.168.10.147:5000/api', "edge")

    # print(response_from_fog)
    
    # Process the data and generate a response
    # response = {'message': 'Data received successfully', 'data': data}
    # return jsonify(response)

    if 'message' in data and data['message'] == 'negotiate':
        script_path = "/root/thesis/edge/bash.sh" 
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
        
        negotiation = "unsuccessful"
        for node_name, values in node_data.items():
            if int(values['CPU%'].rstrip('%')) < 50 and int(values['MEMORY%'].rstrip('%')) < 50:
                print(f"Node: {node_name} -> CPU usage is {values['CPU%']} and memory usage is {values['MEMORY%']}")
                negotiation = "successful"
            else:
                print(f"Node: {node_name} -> CPU usage is {values['CPU%']} and memory usage is {values['MEMORY%']}")

        # negotiation with fog
        response_from_fog = send_api_request_fog('http://192.168.10.147:5000/api', "negotiate")
        print(response_from_fog)

        return jsonify({'reply': negotiation, 'data': node_data})
    else:
        return jsonify({'reply': 'invalid message'})


def send_api_request_fog(url, data):
        response = requests.post(url, json=data)
        return response.json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)