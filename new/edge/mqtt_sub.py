import paho.mqtt.client as mqtt
import time

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

# Callback function to execute when a message is received
def on_message(client, userdata, message):
    message = message.payload.decode()
    if message != "Hello MQTT":
        message = int(message)    
        print("Received message:", message)
        print("Received message:", type(message))

# Create MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Start the MQTT loop to process incoming messages
client.loop_start()

# Keep the script running to receive messages
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Disconnect from broker when interrupted
    client.disconnect()
    client.loop_stop()
