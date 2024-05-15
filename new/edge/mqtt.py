import paho.mqtt.client as mqtt
import time
import random

# MQTT broker address and port
broker_address = "broker.hivemq.com"
broker_port = 1883

# MQTT topic to publish to
topic = "test/topic"

# Callback function to execute when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")

# Create MQTT client instance
client = mqtt.Client()

# Set callback function for when the client connects to the broker
client.on_connect = on_connect

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Loop to continuously publish random numbers
try:
    while True:
        # Generate a random number between 0 and 100
        random_number = random.randint(0, 100)

        # Publish the random number to the MQTT topic
        client.publish(topic, random_number)

        # Print the published message
        print("Published random number:", random_number)

        # Wait for a short interval before publishing the next message
        time.sleep(1)
except KeyboardInterrupt:
    # Disconnect from broker when interrupted
    client.disconnect()
