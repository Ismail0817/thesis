import json
import time
import requests
import paho.mqtt.client as mqtt

# MQTT Broker Details
mqtt_broker = "broker.hivemq.com"
mqtt_port = 1883
mqtt_topic = "test/weather"

# API Endpoint
api_endpoint = "http://192.168.10.145:5000/container_api"

# Global variable to store received data
received_data = []

# Callback function for when a message is received from MQTT
def on_message(client, userdata, message):
    global received_data
    payload = json.loads(message.payload.decode("utf-8"))
    
    # Check for NaN values
    if "NaN" not in payload.values():
        received_data.append(payload)
    else:
        print("Received message contains NaN value, discarding...")

# Function to send data to API endpoint
def send_data_to_api():
    global received_data
    if received_data:
        consolidated_data = json.dumps(received_data)
        response = requests.post(api_endpoint, json=consolidated_data)
        if response.status_code == 200:
            print("Data sent successfully to API")
        else:
            print("Failed to send data to API")
    else:
        print("No data to send")

# MQTT Client setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.subscribe(mqtt_topic)
mqtt_client.loop_start()

# Main loop
try:
    while True:
        time.sleep(15)  # Wait for 15 seconds
        send_data_to_api()
        received_data = []  # Clear the received data after sending
        break
except KeyboardInterrupt:
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
