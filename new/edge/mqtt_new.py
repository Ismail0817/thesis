import paho.mqtt.client as mqtt
import time
import random
import json

# MQTT broker address and port
broker_address = "broker.hivemq.com"
broker_port = 1883

# MQTT topic to publish to
topic = "test/weather"

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

# Loop to continuously publish weather data
try:
    while True:
        # Generate random weather attributes
        outlook = random.choice(['sunny', 'cloudy', 'rainy'])
        temperature = round(random.uniform(15, 35), 2)  # Random temperature between 15°C and 35°C
        windy = random.choice([True, False])
        humidity = round(random.uniform(30, 90), 2)  # Random humidity between 30% and 90%

        # Generate "NaN" value for one of the weather attributes every 10 seconds
        if int(time.time()) % 10 == 0:
            attribute_to_nan = random.choice(['temperature', 'windy', 'humidity'])
            if attribute_to_nan == 'temperature':
                temperature = "NaN"
            elif attribute_to_nan == 'windy':
                windy = "NaN"
            elif attribute_to_nan == 'humidity':
                humidity = "NaN"

        # Create a dictionary to hold the weather data
        weather_data = {
            "outlook": outlook,
            "temperature": temperature,
            "windy": windy,
            "humidity": humidity
        }

        # Convert the weather data dictionary to JSON format
        json_data = json.dumps(weather_data)

        # Publish the JSON data to the MQTT topic
        client.publish(topic, json_data)

        # Print the published message
        print("Published weather data:", json_data)

        # Wait for a short interval before publishing the next message
        time.sleep(1)  # Adjust the interval as needed
except KeyboardInterrupt:
    # Disconnect from broker when interrupted
    client.disconnect()
