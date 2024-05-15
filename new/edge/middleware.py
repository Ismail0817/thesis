from flask import Flask, request

app = Flask(__name__)

@app.route('/container_api', methods=['POST'])
def handle_container_api_request():
    # Logic for handling another API request
    # ...
    request_data = request.get_json()

    # Extract the request type from the request data
    res = request_data.get('message')
    task = request_data.get('task')
    print(res)
    print(task)
    return {'result': 'Data received in middleware API'}

@app.route('/api', methods=['POST'])
def handle_api_request():
    request_data = request.get_json()

    # Extract the request type from the request data
    task_type = request_data.get('message')
    print(task_type)

    if task_type == 'task1':
        # Perform task 1
        result = perform_task1(request_data)
    elif task_type == 'task2':
        # Perform task 2
        result = perform_task2(request_data)
    elif task_type == 'task3':
        # Perform task 3
        result = perform_task3(request_data)
    else:
        # Invalid request type
        result = {'error': 'Invalid request type'}

    return result

def perform_task1(request_data):
    # Logic for task 1
    # ...
    result = negotiate_edge()
    print(result)
    print(request_data.get('message'))
    if result == "success":
        # return {'result': 'Task 1 completed'}
        deploy_pod(request_data.get('message'))
        deploy_service(request_data.get('message'))
        return {'result': 'Task 1 deployed successfully wait for result'}
    else:
        return {'result': 'Task 1 failed because of edge negotiation failure'}

def perform_task2(request_data):
    # Logic for task 2
    # ...
    result = negotiate_edge()
    print(result)
    if result == "success":
        deploy_pod("task2")
        deploy_service("task2")
        return {'result': 'Task 2 deployed successfully in edge.  Wait for result from edge and fog.'}
    else:
        return {'result': 'Task 2 failed because of edge negotiation failure'}

def perform_task3(request_data):
    # Logic for task 3
    # ...

    return {'result': 'Task 3 completed'}

def negotiate_edge():
    return "success"

def deploy_pod(task):
    if task == "task1":
        print("pod deployed")
    elif task == "task2":
        print("pod deployed")
    elif task == "task3":
        print("pod deployed")
    
def deploy_service(task):
    if task == "task1":
        print("service deployed")
    elif task == "task2":
        print("service deployed")
    elif task == "task3":
        print("service deployed")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)