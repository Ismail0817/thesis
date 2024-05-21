import paho.mqtt.client as mqtt
import json
import time

# Define the topics based on the column names
topics = [
    "temperaturec",
    "pm10",
    "pm25",
    "nc05",
    "nc10",
    "fire_alarm"
]

# Dictionary to store received data
received_data = {topic: [] for topic in topics}

# Callback when a message is received
def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode("utf-8"))
    topic = message.topic
    received_data[topic].append(payload)
    print(f"Received message from {topic}: {payload}")

# MQTT setup
broker_address = "broker.hivemq.com"  # Replace with your broker address
client = mqtt.Client()
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, 1883, 60)

# Subscribe to all topics
for topic in topics:
    client.subscribe(topic)
    print(f"Subscribed to {topic}")

# Start the MQTT loop in a non-blocking way
client.loop_start()

# Collect data for 5 seconds
time.sleep(10)

# Stop the MQTT loop
client.loop_stop()

# Merge data by utc
merged_data = {}

for topic, messages in received_data.items():
    for message in messages:
        utc = message['utc']
        if utc not in merged_data:
            merged_data[utc] = {}
        # Update merged data with message values for all topics
        merged_data[utc].update(message)

# Convert the merged data to a list of dictionaries sorted by utc
merged_list = [{'utc': utc, **values} for utc, values in merged_data.items()]
merged_list.sort(key=lambda x: x['utc'])

print("Merge data:")

# Print the merged data
print(json.dumps(merged_list, indent=4))

print("Data collection completed and saved to merged_sensor_data.json")
client.disconnect()
