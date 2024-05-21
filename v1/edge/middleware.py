import subprocess
from flask import Flask, request
import requests
import yaml
from kubernetes import client, config


app = Flask(__name__)

@app.route('/container_api', methods=['POST'])
def handle_container_api_request():
    # Logic for handling another API request
    # ...
    request_data = request.get_json()
    print(request_data)
    # return {'result': 'Data received in container API'}
    # Extract the request type from the request data
    res = request_data.get('message')
    # task = request_data.get('task')
    print(res)
    # print(task)
    if task_type == 'task1':
        response = requests.post('http://192.168.10.148:5003/api', json=request_data)
        print(response.text)
    elif task_type == 'task2':
        payload = {'message': request_data, 'task': 'task2'}
        response = requests.post('http://192.168.10.146:5000/api', json=payload)
        print(response.text)
        payload = {'message': "task 2 started", 'task': 'task2'}
        response = requests.post('http://192.168.10.148:5003/api', json=payload)
        print(response.text)
        # print("task2 is due")
    elif task_type == 'task3':
        payload = {'message': request_data, 'task': 'task3'}
        response = requests.post('http://192.168.10.146:5000/api', json=payload)
        print(response.text)
        payload = {'message': "task 2 started", 'task': 'task3'}
        response = requests.post('http://192.168.10.148:5003/api', json=payload)
        print(response.text)
        # print("task2 is due")
    return {'result': 'Data received in middleware API'}

@app.route('/api', methods=['POST'])
def handle_api_request():
    request_data = request.get_json()
    global task_type
    # Extract the request type from the request data
    task_type = request_data.get('message')
    # print(task_type)

    if task_type == 'task1' or task_type == 'task2' or task_type == 'task3':
        # Perform task 1
        result = perform_task1(request_data)
    else:
        # Invalid request type
        result = {'error': 'Invalid request type'}

    return result

def perform_task1(request_data):
    # Logic for task 1
    # ...
    result = negotiate_edge()
    # print(result)
    print(request_data.get('message'))
    if result == "success":
        # return {'result': 'Task 1 completed'}
        deploy_pod()
        # deploy_service(request_data.get('message'))
        return {'result': 'Task 1 deployed successfully wait for result'}
    else:
        return {'result': 'Task 1 failed because of edge negotiation failure'}


def negotiate_edge():
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
        if int(values['CPU%'].rstrip('%')) < 50 and int(values['MEMORY%'].rstrip('%')) < 70:
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

    # Create Kubernetes API client for batch operations
    batch_v1 = client.BatchV1Api()

    with open("manifests/job.yaml", "r") as file:
        job_manifest = yaml.safe_load(file)
        try:
            # # Set the desired name for the deployment and pod
            # deployment_manifest['metadata']['name'] = "edge-deployment"
            # deployment_manifest['spec']['template']['metadata']['name'] = "edge-pod"
            
            # Create the job in the "default" namespace
            batch_v1.create_namespaced_job(
                body=job_manifest, namespace="default"
            )
            print("Deployment created successfully!")
        except Exception as e:
            print(f"Error creating Deployment: {e}")

            # print("pod deployed")
    
def deploy_service(task):
    if task == "task1":
        print("service deployed")
    elif task == "task2":
        print("service deployed")
    elif task == "task3":
        print("service deployed")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)