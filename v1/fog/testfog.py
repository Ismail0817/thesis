import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

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

df = pd.DataFrame(data)
print(df, "\n")

# Convert 'windy' from boolean to integer
df['windy'] = df['windy'].astype(int)
print(df, "\n")

# # Normalize or standardize numerical values
scaler = StandardScaler()
df[['temperature', 'humidity']] = scaler.fit_transform(df[['temperature', 'humidity']])
print(df, "\n") 

# # Encode categorical variables
encoder = OneHotEncoder(sparse_output=False)
outlook_encoded = encoder.fit_transform(df[['outlook']])
print(outlook_encoded, "\n")

# # Convert the encoded categorical columns to a DataFrame
outlook_df = pd.DataFrame(outlook_encoded, columns=encoder.get_feature_names_out(['outlook']))
print(outlook_df, "\n") 

# # Concatenate the encoded categorical columns with the original DataFrame
df = pd.concat([df, outlook_df], axis=1)
print(df, "\n") 

# # Drop the original 'outlook' column
df.drop('outlook', axis=1, inplace=True)
print(df, "\n") 
