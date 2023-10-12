import requests 
from dotenv import load_dotenv
import os
load_dotenv(".env")
WEATHERAPI_KEY = os.environ.get("WEATHERAPI_KEY")

def getForecastAPI():
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q=95070&days=2&aqi=no&alerts=no")
    data = response.json()
    precipitation = data['forecast']['forecastday'][0]['day']['totalprecip_in']
    print(precipitation)
    return str(precipitation)

getForecastAPI()