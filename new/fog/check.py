from kubernetes import client, config
import time

def check_deployment_ready(deployment_name, namespace='default'):
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")
    api_instance = client.AppsV1Api()
    while True:
        try:
            deployment = api_instance.read_namespaced_deployment(deployment_name, namespace)
            if deployment.status.available_replicas == deployment.spec.replicas:
                return True
        except Exception as e:
            print(f"Error checking deployment: {e}")
        time.sleep(1)

def check_service_ready(service_name, namespace='default'):
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")
    api_instance = client.CoreV1Api()
    while True:
        try:
            service = api_instance.read_namespaced_service(service_name, namespace)
            if service.status.load_balancer.ingress:
                return True
        except Exception as e:
            print(f"Error checking service: {e}")
        time.sleep(1)

if __name__ == "__main__":
    deployment_name = "fog"
    service_name = "fog-service"

    print("Waiting for Deployment to become ready...")
    check_deployment_ready(deployment_name)
    print("Deployment is ready.")

    print("Waiting for Service to become ready...")
    check_service_ready(service_name)
    print("Service is ready.")
