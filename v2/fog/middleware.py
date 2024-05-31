import json
import subprocess
import threading
import time
from flask import Flask, request
import psutil
import requests
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


app = Flask(__name__)

@app.route('/api', methods=['POST'])
def handle_api_request():
    request_data = request.get_json()
    global task_type

    # print(request_data)
    # Extract the request type from the request data
    # task_type = request_data.get('task')
    
    message_json = request_data['message']
    task = request_data['task']


    # print("Message:", message_json)
    print("Task:", task)
    # return {'result': 'data received in fog middleware API'}
    # print(request_data)
    # print(type(request_data))
    # print(request_data.get('message'))

    if task == 'task2' or task == 'task3':
        # Perform task 2
        result = negotiate_fog()
        # print(result) 
        # return {'result': 'data received in fog middleware API'}  
        if result == "success":
            threading.Thread(target=perform_task2, args=(message_json,task)).start()
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
    # print("inside thread\nsending data to fog container\n")
    # print("Message:", message)
    # print("Task:", task_type)

    # Monitor initial CPU and memory usage before orchestration
    initial_cpu, initial_memory = monitor_resources()
    print(f"Initial CPU Usage: {initial_cpu}%")
    print(f"Initial Memory Usage: {initial_memory}%")

    print("Starting orchestration...")
    start_time = time.time()

    deploy_pod()
    deploy_service()
    
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

    # Define namespace, Job name, and Service name
    namespace = 'default'
    deployment_name = 'fog'
    service_name = 'fog-service'
    flask_ready_log_entry = 'Running on all addresses'

    # Check Job, Pod, and Service status
    deployment_ready = False
    service_ready = False
    flask_ready = False

    while not deployment_ready or not service_ready:
        deployment_ready = check_deployment_status(namespace, deployment_name) and check_pod_status(namespace, deployment_name)
        service_ready = check_service_status(namespace, service_name)

        # Collect CPU and memory usage data during orchestration
        cpu_usage, memory_usage = monitor_resources()
        # print(f"CPU Usage during orchestration: {cpu_usage}%")
        # print(f"Memory Usage during orchestration: {memory_usage}%")
        print(f"During Orchestration - Timestamp: {time.time()}, CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")

        # print(f"Deployment ready: {deployment_ready}, Service ready: {service_ready}")
        # if not deployment_ready or not service_ready:
        #     print("Waiting for Deployment and Service to be ready...")

    print("Deployment and Service are ready. Checking Flask server status...")

    end_time = time.time()
    orchestration_time = end_time - start_time
    print("Orchestration Time:", orchestration_time) 

    # Fetch the Pod name
    pod_name = None
    pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}")
    if pods.items:
        pod_name = pods.items[0].metadata.name

    # Check Flask server readiness
    while not flask_ready:
        flask_ready = check_flask_ready(namespace, pod_name, flask_ready_log_entry)
        # if not flask_ready:
        #     print("Waiting for Flask server to be ready...")

    print("Flask server is ready. Proceeding to send data.")

    end_time = time.time()
    orchestration_time = end_time - start_time
    print("Orchestration Time + Flask ready time:", orchestration_time)  

    # Send data to the pod API endpoint
    response = requests.post("http://192.168.1.146:30234/preprocess", json=message)
    print(response.text)

    if task_type == 'task2':
        payload = {'message': response.text, 'task': 'task2'}
        response = requests.post('http://192.168.10.148:5003/api', json=payload)
        # Print the response from the server
        print(response.text)
    elif task_type == 'task3':
        payload = {'message': response.text, 'task': 'task3'}
        response = requests.post('http://192.168.10.147:5000/api', json=payload)
        print(response.text)
        payload = {'message': "task 3 started", 'task': 'task3'}
        response = requests.post('http://192.168.10.148:5003/api', json=payload)
        print(response.text)
        # print("task 3 is due")
    

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


config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")
# Initialize API clients
app_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

def check_deployment_status(namespace, deployment_name):
    try:
        deployment = app_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        if deployment.status.ready_replicas == deployment.status.replicas:
            # print("Deployment is ready.")
            return True
        else:
            # print("Deployment is not ready.")
            return False
    except ApiException as e:
        print(f"Exception when reading Deployment: {e}")
        return False
    
def check_pod_status(namespace, deployment_name):
    try:
        pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}")
        for pod in pods.items:
            if pod.status.phase == 'Running':
                # print(f"Pod {pod.metadata.name} is running.")
                return True
            # elif pod.status.phase == 'Pending':
            #     print(f"Pod {pod.metadata.name} is pending.")
            # elif pod.status.phase == 'Failed':
            #     print(f"Pod {pod.metadata.name} has failed.")
        return False
    except ApiException as e:
        print(f"Exception when listing Pods: {e}")
        return False

def check_service_status(namespace, service_name):
    try:
        service = core_v1.read_namespaced_service(name=service_name, namespace=namespace)
        if service.spec.type == 'LoadBalancer':
            node_port = service.spec.ports[0].node_port
            # print(f"Service is up with NodePort: {node_port}")
            return True
        else:
            print("Service is not of type NodePort.")
            return False
    except ApiException as e:
        print(f"Exception when reading Service: {e}")
        return False

def check_flask_ready(namespace, pod_name, log_entry):
    try:
        logs = core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
        if log_entry in logs:
            # print("Flask server is ready.")
            return True
        else:
            return False
    except ApiException as e:
        print(f"Exception when reading Pod logs: {e}")
        return False

def monitor_resources():
    # Function to capture CPU and memory usage
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory_info = psutil.virtual_memory()
    return cpu_usage, memory_info.percent


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)