from kubernetes import client, config
from kubernetes.client.rest import ApiException

def check_pod_status(namespace='default'):
    # Load kubeconfig
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

    # Create an instance of the API class
    v1 = client.CoreV1Api()

    try:
        # List all pods in the specified namespace
        pod_list = v1.list_namespaced_pod(namespace)
        for pod in pod_list.items:
            name = pod.metadata.name
            status = pod.status.phase
            print(f"Pod Name: {name}, Status: {status}")
        print (name)

    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

if __name__ == "__main__":
    check_pod_status(namespace='default')
