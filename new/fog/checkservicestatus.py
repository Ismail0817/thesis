from kubernetes import client, config

def get_service_status(namespace, service_name):
    # Load the kubeconfig file (ensure this is set up correctly to access your cluster)
    config.load_kube_config()

    # Create an instance of the CoreV1Api
    v1 = client.CoreV1Api()

    # Get the service object
    try:
        service = v1.read_namespaced_service(name=service_name, namespace=namespace)
        # Print the service status
        print(f"Service '{service_name}' in namespace '{namespace}' status:")
        print(f"Type: {service.spec.type}")
        print(f"Cluster IP: {service.spec.cluster_ip}")
        print(f"External IPs: {service.status.load_balancer.ingress if service.status.load_balancer else 'None'}")
        print(f"Ports: {service.spec.ports}")
    except client.exceptions.ApiException as e:
        print(f"Exception when calling CoreV1Api->read_namespaced_service: {e}")

# Usage example
get_service_status('default', 'fog-service')
