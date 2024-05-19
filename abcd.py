import requests
import json

# Data to be sent to the API
data = [
    {'outlook': 'cloudy', 'temperature': 23.64, 'windy': True, 'humidity': 34.6},
    {'outlook': 'sunny', 'temperature': 21.76, 'windy': True, 'humidity': 30.17},
    {'outlook': 'rainy', 'temperature': 27.17, 'windy': False, 'humidity': 67.3},
    {'outlook': 'rainy', 'temperature': 30.03, 'windy': True, 'humidity': 33.72},
    {'outlook': 'sunny', 'temperature': 25.44, 'windy': True, 'humidity': 71.09},
    {'outlook': 'cloudy', 'temperature': 28.11, 'windy': False, 'humidity': 51.24},
    {'outlook': 'cloudy', 'temperature': 33.45, 'windy': False, 'humidity': 41.98},
    {'outlook': 'sunny', 'temperature': 31.56, 'windy': True, 'humidity': 74.83},
    {'outlook': 'sunny', 'temperature': 31.86, 'windy': False, 'humidity': 86.76},
    {'outlook': 'rainy', 'temperature': 21.61, 'windy': False, 'humidity': 83.69},
    {'outlook': 'sunny', 'temperature': 30.78, 'windy': False, 'humidity': 84.28},
    {'outlook': 'rainy', 'temperature': 24.72, 'windy': True, 'humidity': 54.64},
    {'outlook': 'sunny', 'temperature': 28.91, 'windy': False, 'humidity': 72.32}
]

# Send data to the API endpoint
response = requests.post("http://192.168.10.147:5005/preprocess", json=data)

# Print the response from the server
print(response.json())