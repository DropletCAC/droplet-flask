import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--emulator', action='store_true')
args = parser.parse_args()

if args.emulator:
  print("Starting in emulator mode...")
  os.environ["FIRESTORE_EMULATOR_HOST"]="localhost:8080"
  os.environ["GCLOUD_PROJECT"]="droplet-54c51"

from flask import Flask, request
import requests 
import json
from datetime import datetime, timedelta
from leak_detection import detect_leak, add_leak
from dotenv import load_dotenv
load_dotenv(".env")


app = Flask(__name__)
WEATHERAPI_KEY = os.environ.get("WEATHERAPI_KEY")
print(WEATHERAPI_KEY)


@app.route('/leak', methods=['GET'])
def leak():
    if request.method == "GET":
        user, section, month, day, hour = request.args.get('user'), request.args.get('section'), request.args.get('month'), request.args.get('day'), request.args.get('hour')
        leak_date = datetime(2023, int(month), int(day), int(hour))
        print(user, section, leak_date)
        
        leak_data = detect_leak(user, section, leak_date)
       
        # if leak_data['leak']:
        #     print("Leak detected, adding")
        #     add_leak(user, leak_data)
            
        return (leak_data)
    

def getForecast():
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q=95070&days=2&aqi=no&alerts=no")
    data = response.json()
    
    precipitation = 0
    for forecast in data['forecast']['forecastday'][1]['hour']:
        precipitation += forecast['precip_in']
        
    return str(precipitation)


@app.route('/rain', methods=['GET'])
def rain():
    if request.method == "GET":
        return getForecast()
    

if __name__ == "__main__":
    app.run(host="0.0.0.0")