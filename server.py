from flask import Flask, request
import requests 
import os
import datetime
from leak_detection import detect_leak

app = Flask(__name__)
WEATHERAPI_KEY = os.environ.get("WEATHERAPI_KEY")
print(WEATHERAPI_KEY)


@app.route('/leak', methods=['GET'])
def leak():
    if request.method == "GET":
        user, section, month, day = request.args.get('user'), request.args.get('section'), request.args.get('month'), request.args.get('day')
        print(user, section, month, day)
        is_leak = detect_leak(user, section, month=int(month), day=int(day))
        return str(is_leak)
    

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