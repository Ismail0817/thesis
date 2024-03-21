import yaml
from kubernetes import client, config

def deploy_pod():
    # Load kubeconfig file to authenticate with the Kubernetes cluster
    config.load_kube_config(config_file= "/etc/rancher/k3s/k3s.yaml")

    # Load all YAML documents from the file
    with open("deployment.yaml", "r") as file:
        deployment_manifests = yaml.load_all(file, Loader=yaml.SafeLoader)

        # Create Kubernetes API client
        apps_v1 = client.AppsV1Api()

        # Create the Deployments
        for deployment_manifest in deployment_manifests:
            try:
                apps_v1.create_namespaced_deployment(
                    body=deployment_manifest, namespace="default"
                )
                print("Deployment created successfully!")
            except Exception as e:
                print(f"Error creating Deployment: {e}")

if __name__ == "__main__":
    deploy_pod()
