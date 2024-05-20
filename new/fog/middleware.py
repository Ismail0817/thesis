import json
import subprocess
import threading
import time
from flask import Flask, request
import requests
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


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
            threading.Thread(target=perform_task2, args=(message,task)).start()
            return {'result': 'Task 2 deployed successfully wait for result'}
        else:
            return {'result': 'Task 2 failed because of fog negotiation failure'}
    else:
        # Invalid request type
        return {'error': 'Invalid request type'}

    # return {'result': 'data received in fog middleware API'}

def perform_task2(message,task_type):
    # Logic for task 2
    # ...
    print("inside thread\n sending data to fog container\n")
    print("Message:", task_type)
    deploy_pod()
    deploy_service()
    
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")
    # Create an instance of the API class
    api_instance = client.AppsV1Api()
    namespace='default'
    service_name='fog-service'
    deployment_name='fog'
    while True:
        try:
            deployment = api_instance.read_namespaced_deployment(deployment_name, namespace)
            if deployment.status.available_replicas == deployment.spec.replicas:
                print("Deployment is ready")
                break
        except Exception as e:
            print(f"Error checking deployment: {e}")
        # time.sleep(1)
    
    api_instance = client.CoreV1Api()
    while True:
        try:
            service = api_instance.read_namespaced_service(service_name, namespace)
            if service.status.load_balancer.ingress:
                print("Service is ready")
                break
        except Exception as e:
            print(f"Error checking service: {e}")
        # time.sleep(1)
        
    time.sleep(3)
    # Send data to the pod API endpoint
    response = requests.post("http://192.168.1.146:30234/preprocess", json=message)
    print(response.text)
    payload = {'message': response.text, 'task': 'task2'}
    response = requests.post('http://192.168.10.148:5003/api', json=payload)

    # Print the response from the server
    print(response.text)
    # # print(request_data.get('message'))
    

def negotiate_fog():
    script_path = "/home/admin/github/thesis/new/edge/bash.sh" 
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

def deploy_pod():
    # Load kubeconfig file to authenticate with the Kubernetes cluster
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

    # Create Kubernetes API client
    apps_v1 = client.AppsV1Api()

    with open("manifests/deployment.yaml", "r") as file:
        deployment_manifest = yaml.safe_load(file)
        try:
            # # Set the desired name for the deployment and pod
            # deployment_manifest['metadata']['name'] = "edge-deployment"
            # deployment_manifest['spec']['template']['metadata']['name'] = "edge-pod"
            
            # Create the deployment in the "default" namespace
            apps_v1.create_namespaced_deployment(
                body=deployment_manifest, namespace="default"
            )
            print("Deployment created successfully!")
        except Exception as e:
            print(f"Error creating Deployment: {e}")

            # print("pod deployed")

def deploy_service():
    # Load kubeconfig file to authenticate with the Kubernetes cluster
    config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")

    # Load YAML file containing the service manifest
    with open("manifests/service.yaml", "r") as file:
        service_manifest = yaml.safe_load(file)

    # Create Kubernetes API client
    core_v1 = client.CoreV1Api()

    try:
        # Create the Service
        core_v1.create_namespaced_service(
            body=service_manifest, namespace="default"
        )
        print("Service created successfully!")
    except Exception as e:
        print(f"Error creating Service: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)