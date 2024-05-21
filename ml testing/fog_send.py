import requests
import json

# Sample data
data = [
    {'utc': 1654738164.0, 'Temperature[C]': -7.53, 'PM1.0': 2.32, 'PM2.5': 2.41, 'NC0.5': 15.97, 'NC1.0': 2.491, 'Fire Alarm': 1.0},
    {'utc': 1654738165.0, 'Temperature[C]': -7.536, 'PM1.0': 2.31, 'PM2.5': 2.4, 'NC0.5': 15.93, 'NC1.0': 2.484, 'Fire Alarm': 1.0},
    {'utc': 1654738166.0, 'Temperature[C]': -7.541, 'PM1.0': 2.3, 'PM2.5': 2.39, 'NC0.5': 15.8, 'NC1.0': 2.464, 'Fire Alarm': 1.0},
    {'utc': 1654738167.0, 'Temperature[C]': -7.547, 'PM1.0': 2.28, 'PM2.5': 2.37, 'NC0.5': 15.68, 'NC1.0': 2.444, 'Fire Alarm': 1.0},
    {'utc': 1654738168.0, 'Temperature[C]': -7.552, 'PM1.0': 2.29, 'PM2.5': 2.38, 'NC0.5': 15.76, 'NC1.0': 2.458, 'Fire Alarm': 1.0},
    {'utc': 1654738169.0, 'Temperature[C]': -7.558}
]

# API endpoint URL
url = "http://192.168.10.243:5005/preprocess"

# Sending POST request to the API endpoint
response = requests.post(url, json=data)

# Print the response from the server
print(response.status_code)
print(response.json())
