from flask import Flask, request, jsonify
import yaml
from kubernetes import client, config
import subprocess

app = Flask(__name__)

# Load kubeconfig file to authenticate with the Kubernetes cluster
config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

# Create Kubernetes API client
apps_v1 = client.AppsV1Api()

def deploy_pod():
    # Load kubeconfig file to authenticate with the Kubernetes cluster
    # config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

    # Load all YAML documents from the file
    with open("manifests/deployment.yaml", "r") as file:
        deployment_manifests = yaml.load_all(file, Loader=yaml.SafeLoader)

        # Create Kubernetes API client
        # apps_v1 = client.AppsV1Api()

        # Create the Deployments
        for deployment_manifest in deployment_manifests:
            try:
                apps_v1.create_namespaced_deployment(
                    body=deployment_manifest, namespace="default"
                )
                print("Deployment created successfully!")
            except Exception as e:
                print(f"Error creating Deployment: {e}")

def deploy_external_service():
    # Load kubeconfig file to authenticate with the Kubernetes cluster
    # config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")

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
    # # Process the data and generate a response
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

        return jsonify({'reply': negotiation, 'data': node_data})
    
    elif 'message' in data and data['message'] == 'deploy_pod':
        # If the message is 'hello', reply with 'hello world'
        deploy_pod()
        return jsonify({'reply': 'pod deployed'})
    
    elif 'message' in data and data['message'] == 'deploy_service':
        # If the message is not as expected, return an error
        deploy_external_service()
        return jsonify({'reply': 'service deployed'})

    else:
        return jsonify({'reply': 'invalid message'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)