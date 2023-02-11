from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import pickle
import numpy as np
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False
app.secret_key = uuid.uuid4().hex
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
    ct = carbon_t['property']['carbon_total'][0]['value']["value"]
    url = "https://api.isda-africa.com/v1/soilproperty?key=AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4&lat={}&lon={}&property={}&depth=0-20".format(latitude, longitude, 'carbon_organic')
    carbon_o = requests.get(url).json()
    co = carbon_o['property']['carbon_organic'][0]['value']["value"]
    pred = anf.predict(np.array([[ct, co]]))
    flash('The predicted soil pH value is %2.2f'% pred[0][0])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = uuid.uuid4().hex
    app.run(debug=False, port=5000)