import subprocess
import threading
import time
from flask import Flask, request
import requests
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


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
    # print(res)
    # print(task)
    if task_type == 'task1':
        response = requests.post('http://192.168.10.148:5003/api', json=request_data)
        print(response.text)
    elif task_type == 'task2':
        payload = {'message': res, 'task': 'task2'}
        response = requests.post('http://192.168.10.146:5000/api', json=payload)
        print(response.text)
        payload = {'message': "task 2 started", 'task': 'task2'}
        response = requests.post('http://192.168.10.148:5003/api', json=payload)
        print(response.text)
        # print("task2 is due")
    elif task_type == 'task3':
        payload = {'message': res, 'task': 'task3'}
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
    time = request_data.get('time')
    # print(task_type)

    if task_type == 'task1' or task_type == 'task2' or task_type == 'task3':
        # Perform task 1
        result = negotiate_edge()
        print(result) 
        # return {'result': 'data received in fog middleware API'}  
        if result == "success":
            threading.Thread(target=perform_task1, args=(task_type,time)).start()
            return {'result': 'Task 1 deployed successfully wait for result'}
        else:
            return {'result': 'Task 1 failed because of edge negotiation failure'}
    else:
        # Invalid request type
        return {'error': 'Invalid request type'}

    # return {'result': 'Task 2 deployed successfully wait for result'}

def perform_task1(task_type,collection_time):
    # Logic for task 1
    # ...

    print("inside thread\n sending data to fog container\n")
    print("Time:", collection_time)
    print("Task:", task_type)
    deploy_pod()
    deploy_service()

    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

    # Define namespace, Job name, and Service name
    namespace = 'default'
    job_name = 'run-once-job-edge'
    service_name = 'run-once-job-edge-service'

    # Check Job, Pod, and Service status
    job_ready = False
    service_ready = False

    while not job_ready or not service_ready:
        job_ready = check_job_status(namespace, job_name) and check_pod_status(namespace, job_name)
        service_ready = check_service_status(namespace, service_name)
        if not job_ready or not service_ready:
            print("Waiting for Job and Service to be ready...")
            time.sleep(5)  # Wait before checking again

    print("Job and Service are ready. Proceeding to send data.")

    
        



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
batch_v1 = client.BatchV1Api()
core_v1 = client.CoreV1Api()
def check_job_status(namespace, job_name):
    try:
        job = batch_v1.read_namespaced_job(name=job_name, namespace=namespace)
        if job.status.succeeded:
            print("Job succeeded.")
            return True
        elif job.status.failed:
            print("Job failed.")
            return False
        elif job.status.active:
            print("Job is still active.")
            return True
    except ApiException as e:
        print(f"Exception when reading Job: {e}")
        return False

def check_pod_status(namespace, job_name):
    try:
        pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")
        for pod in pods.items:
            if pod.status.phase == 'Running':
                print(f"Pod {pod.metadata.name} is running.")
                return True
            elif pod.status.phase == 'Pending':
                print(f"Pod {pod.metadata.name} is pending.")
            elif pod.status.phase == 'Failed':
                print(f"Pod {pod.metadata.name} has failed.")
        return False
    except ApiException as e:
        print(f"Exception when listing Pods: {e}")
        return False

def check_service_status(namespace, service_name):
    try:
        service = core_v1.read_namespaced_service(name=service_name, namespace=namespace)
        if service.spec.type == 'NodePort':
            node_port = service.spec.ports[0].node_port
            print(f"Service is up with NodePort: {node_port}")
            return True
        else:
            print("Service is not of type NodePort.")
            return False
    except ApiException as e:
        print(f"Exception when reading Service: {e}")
        return False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)