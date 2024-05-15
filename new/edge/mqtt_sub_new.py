import paho.mqtt.client as mqtt
import time
import requests

# MQTT broker address and port
broker_address = "broker.hivemq.com"
broker_port = 1883

# MQTT topic to subscribe to
topic = "test/topic"

# Callback function to execute when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # Subscribe to the topic when connected
        client.subscribe(topic)
    else:
        print("Connection failed")

# Variable to store the sum of numbers received
sum_of_numbers = 0

# Callback function to execute when a message is received
def on_message(client, userdata, message):
    global sum_of_numbers
    message = message.payload.decode()
    if message != "Hello MQTT":
        message = int(message)    
        print("Received message:", message)
        # print("Received message:", type(message))
        sum_of_numbers += message
    # received_number = int(message.payload.decode())
    # print("Received number:", received_number)
    # sum_of_numbers += received_number

# Create MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Start the MQTT loop to process incoming messages
client.loop_start()

# Keep track of time
start_time = time.time()

try:
    while True:
        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # If 10 seconds have elapsed, print the sum and reset sum_of_numbers
        if elapsed_time >= 10:
            print("Sum of numbers received in the last 10 seconds:", sum_of_numbers)
            # Send the total to the API endpoint
            response = requests.post('http://192.168.10.145:5000/container_api', json={'message': sum_of_numbers, 'task': 'task2'})
            if response.status_code == 200:
                print('Total sent to API successfully!', flush=True)
            else:
                print('Failed to send total to API:', response.status_code, flush=True)
            sum_of_numbers = 0
            start_time = time.time()

        time.sleep(1)
except KeyboardInterrupt:
    # Disconnect from broker when interrupted
    client.disconnect()
    client.loop_stop()
