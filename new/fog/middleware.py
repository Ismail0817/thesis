import subprocess
import threading
from flask import Flask, request
import requests
import yaml
from kubernetes import client, config


app = Flask(__name__)

@app.route('/api', methods=['POST'])
def handle_api_request():
    request_data = request.get_json()
    global task_type
    # Extract the request type from the request data
    task_type = request_data.get('task')
    print(task_type)
    print(request_data.get('message'))

    if task_type == 'task2' or task_type == 'task3':
        # Perform task 2
        threading.Thread(target=perform_task2, args=(request_data,)).start()
        result = {'result': 'Task 2 thread started, wait for result'} 
    else:
        # Invalid request type
        result = {'error': 'Invalid request type'}

    return result
    # return {'result': 'data received in fog middleware API'}

def perform_task2(request_data):
    # Logic for task 1
    # ...
    # result = negotiate_edge()
    print("inside thread")
    print(request_data.get('message'))
    # if result == "success":
    #     # return {'result': 'Task 1 completed'}
    #     deploy_pod()
    #     # deploy_service(request_data.get('message'))
    #     return {'result': 'Task 1 deployed successfully wait for result'}
    # else:
    #     return {'result': 'Task 1 failed because of edge negotiation failure'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)