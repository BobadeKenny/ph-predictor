from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import pickle
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.environ.get('secret_key')
anf = pickle.load(open('model/anfis.pkl', 'rb'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/predict", strict_slashes=False, methods=['POST'])
def predict():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    url = "https://api.isda-africa.com/v1/soilproperty?key=AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4&lat={}&lon={}&property={}&depth=0-20".format(latitude, longitude, 'carbon_total')
    carbon_t = requests.get(url).json()
    if carbon_t.get("message") is not None:
        flash(carbon_t["message"])
        return redirect(url_for('index'))
    ct = carbon_t['property']['carbon_total'][0]['value']["value"]
    url = "https://api.isda-africa.com/v1/soilproperty?key=AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4&lat={}&lon={}&property={}&depth=0-20".format(latitude, longitude, 'carbon_organic')
    carbon_o = requests.get(url).json()
    co = carbon_o['property']['carbon_organic'][0]['value']["value"]
    pred = anf.predict(np.array([[ct, co]]))
    if pred < 4.4:
        status = "extremely acidic"
    elif pred < 5.5:
        status = "strongly acidic"
    elif pred < 6.5:
        status = "slightly acidic"
    elif pred < 7.3:
        status = "neutral"
    elif pred < 8.4:
        status = "slightly alkaline"
    else:
        status = "strongly alkaline"
    
    flash('The soil pH is %s with a predicted value of %2.2f'% (status, pred[0][0]))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = os.environ.get('secret_key')
    app.run(debug=True, port=5000)