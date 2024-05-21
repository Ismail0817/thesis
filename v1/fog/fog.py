from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

app = Flask(__name__)

@app.route('/preprocess', methods=['POST'])
def preprocess():
    data = request.get_json()
    print(data, flush=True)
    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    print(df, "\n",  flush=True)

    # Convert 'windy' from boolean to integer
    df['windy'] = df['windy'].astype(int)
    print(df, "\n", flush=True)

    # # Normalize or standardize numerical values
    scaler = StandardScaler()
    df[['temperature', 'humidity']] = scaler.fit_transform(df[['temperature', 'humidity']])
    print(df, "\n", flush=True) 

    # # Encode categorical variables
    encoder = OneHotEncoder(sparse_output=False)
    outlook_encoded = encoder.fit_transform(df[['outlook']])
    print(outlook_encoded, "\n", flush=True)

    # # Convert the encoded categorical columns to a DataFrame
    outlook_df = pd.DataFrame(outlook_encoded, columns=encoder.get_feature_names_out(['outlook']))
    print(outlook_df, "\n", flush=True) 

    # # Concatenate the encoded categorical columns with the original DataFrame
    df = pd.concat([df, outlook_df], axis=1)
    print(df, "\n", flush=True) 

    # # Drop the original 'outlook' column
    df.drop('outlook', axis=1, inplace=True)
    print(df, "\n", flush=True) 

    # Return the preprocessed data
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
