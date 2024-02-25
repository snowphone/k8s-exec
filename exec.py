import argparse

from kubernetes import client
from kubernetes.config import incluster_config
from kubernetes.stream import stream


def find_first_pod_by_selector(
    api_instance: client.CoreV1Api, namespace: str, selector: str
):
    """
    Find the first pod in the specified namespace that matches the given selector.
    This assumes your deployment's label is 'app=photoprism'
    """
    ret = api_instance.list_namespaced_pod(namespace, label_selector=selector)
    if ret.items:
        return ret.items[0]  # Return the first pod
    else:
        return None


def exec_in_pod(
    api_instance: client.CoreV1Api, namespace: str, pod_name: str, command: list[str]
):
    """
    Execute a command in the specified pod.
    """
    resp = stream(
        api_instance.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=command,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
    )
    return resp


def main(args: argparse.Namespace):
    print(args)
    # Loading in-cluster configuration
    incluster_config.load_incluster_config()

    # Defining the API instance
    v1 = client.CoreV1Api()

    namespace = args.namespace
    deployment_name = args.deployment
    command = args.command

    # Find the first pod that matches the deployment's selector
    selector = f"app={deployment_name}"
    pod = find_first_pod_by_selector(v1, namespace, selector)
    print(pod)

    if not pod:
        print("Pod not found.")
        return

    assert pod.metadata
    pod_name = pod.metadata.name
    assert pod_name

    # Execute the command in the pod
    print(f"Executing command in pod: {pod_name}")
    output = exec_in_pod(v1, namespace, pod_name, command)
    print("Command output:", output)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", "-n", default="default")
    parser.add_argument("--deployment", "-d", required=True)
    parser.add_argument("command", nargs='+')

    main(parser.parse_args())
