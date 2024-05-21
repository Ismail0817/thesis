import pickle
from flask import Flask, request, jsonify
import pandas as pd

loaded_model = pickle.load(open("trained_model.pickle",'rb'))
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # print(data, flush=True)
    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    print(df, "\n",  flush=True)
    predictions = loaded_model.predict(df)
    
    response = {'input': data, 'predictions': predictions.tolist()}

    # Return the preprocessed data
    # return jsonify(df.to_dict(orient='records'))
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
