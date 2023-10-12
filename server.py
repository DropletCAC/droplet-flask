import os
import argparse
import firebase_admin
from firebase_admin import credentials, firestore 

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--emulator', action='store_true')
args = parser.parse_args()

if args.emulator:
  print("Starting in emulator mode...")
  os.environ["FIRESTORE_EMULATOR_HOST"]="localhost:8080"
  os.environ["GCLOUD_PROJECT"]="droplet-54c51"

import keras
from flask import Flask, request
import pandas as pd
import requests 
import json
from datetime import datetime, timedelta
from leak_detection import detect_leak, add_leak
from dotenv import load_dotenv
from lstm import model as modelutils
import numpy as np 

load_dotenv(".env")

today = datetime.now()
year = int(today.strftime("%Y"))
month = int(today.strftime("%m"))
day = int(today.strftime("%d"))
hour = int(today.strftime("%H"))

app = Flask(__name__)
WEATHERAPI_KEY = os.environ.get("WEATHERAPI_KEY")
print(WEATHERAPI_KEY)

cred = credentials.Certificate("credentials.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/leak', methods=['GET'])
def leak():
    if request.method == "GET":
        user, section, month, day, hour = request.args.get('user'), request.args.get('section'), request.args.get('month'), request.args.get('day'), request.args.get('hour')
        leak_date = datetime(2023, int(month), int(day), int(hour))
        print(user, section, leak_date)
        
        leak_data = detect_leak(db, user, section, leak_date)
       
        # if leak_data['leak']:
        #     print("Leak detected, adding")
        #     add_leak(user, leak_data)
            
        return (leak_data)
    

def getForecastAPI():
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q=95070&days=2&aqi=no&alerts=no")
    data = response.json()
    precipitation = data['forecast']['forecastday'][0]['day']['totalprecip_in']
    return str(precipitation)


def getForecastLSTM():
    model = keras.models.load_model('./lstm/model3.h5')
    
    past_7_days = []
    
    for history_day in range(day - 6, day + 1):
      print(history_day)
      response = requests.get(f"http://api.weatherapi.com/v1/history.json?key={WEATHERAPI_KEY}&q=95070&dt={year}-{month}-{history_day}")
      data = response.json()['forecast']['forecastday'][0]['day']
      past_7_days.append([data['maxtemp_f'], data['mintemp_f'], data['maxwind_mph'], data['totalprecip_in']])
    
    df = pd.DataFrame(past_7_days)
    print(df)

    X = df.to_numpy()
    X_norm = (X - modelutils.mean_X) / modelutils.std_X    
    
    X_norm = np.array([X_norm])
    print(X_norm)
    predicted_values_norm = model.predict(X_norm)
    predicted_values = modelutils.inverse_normalize_df(predicted_values_norm, modelutils.mean_y, modelutils.std_y)
    print(predicted_values)
    return predicted_values[0][0]
    
    
@app.route('/rain', methods=['GET'])
def rain():
    if request.method == "GET":
        return getForecastAPI()
    

month_data = {
  "Jan": {
    "name": "January",
    "short": "Jan",
    "number": 1,
    "days": 31
  },
  "Feb": {
    "name": "February",
    "short": "Feb",
    "number": 2,
    "days": 28
  },
  "Mar": {
    "name": "March",
    "short": "Mar",
    "number": 3,
    "days": 31
  },
  "Apr": {
    "name": "April",
    "short": "Apr",
    "number": 4,
    "days": 30
  },
  "May": {
    "name": "May",
    "short": "May",
    "number": 5,
    "days": 31
  },
  "Jun": {
    "name": "June",
    "short": "Jun",
    "number": 6,
    "days": 30
  },
  "Jul": {
    "name": "July",
    "short": "Jul",
    "number": 7,
    "days": 31
  },
  "Aug": {
    "name": "August",
    "short": "Aug",
    "number": 8,
    "days": 31
  },
  "Sep": {
    "name": "September",
    "short": "Sep",
    "number": 9,
    "days": 30
  },
  "Oct": {
    "name": "October",
    "short": "Oct",
    "number": 10,
    "days": 31
  },
  "Nov": {
    "name": "November",
    "short": "Nov",
    "number": 11,
    "days": 30
  },
  "Dec": {
    "name": "December",
    "short": "Dec",
    "number": 12,
    "days": 31
  }
}

def generateZeroes(stop_month, stop_day, stop_hour):
    usage_data = {}

    for month_name in month_data:
        
        month_num = str(month_data[month_name]['number'])
        usage_data[month_num] = {}
            
        for day in range(1, month_data[month_name]['days']):

            if (month_data[month_name]['number'] == stop_month):
                if (day == stop_day):
                    day = str(day)
                    usage_data[month_num][day] = [0 for x in range(0, stop_hour)]
                    continue
                
                if (day == stop_day + 1):
                    return usage_data
            
            day = str(day)
            usage_data[month_num][day] = [0 for x in range (0, 24)]
    return usage_data
        
@app.route('/setCurrentUsage', methods=['POST'])
def setCurrentUsage():
    if request.method == "POST":
        user_id, section, usage = request.args.get('user'), request.args.get('section'), request.args.get('usage')
        db.collection("users").document(user_id).collection("meters").document(section).set({
            "currentUsage": usage, 
        })
        
        data = generateZeroes(month, day, hour + 1)
        data[str(month)][str(day)][hour] = usage 

        db.collection("users").document(user_id).collection("meters").document(section).collection("usage").document("2023").set(data)
        
        
        return "ok"


@app.route('/setTankCapacity', methods=['POST'])
def setTankCapacity():
    if request.method == "POST":
        user_id, bucket, volume = request.args.get('user'), request.args.get('bucket'), request.args.get('volume')
        print(user_id, bucket, volume)
        db.collection("users").document(user_id).collection("buckets").document(bucket).update({
            "currentCapacity": round(float(volume), 1), 
        })
        return "ok"
      
      
if __name__ == "__main__":
    app.run(host="0.0.0.0")
    