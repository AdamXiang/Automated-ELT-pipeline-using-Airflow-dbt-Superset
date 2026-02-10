import os

import requests
from dotenv import load_dotenv
import os

load_dotenv('../.env')

api_key = os.getenv('API_KEY')

api_url = f'http://api.weatherstack.com/current?access_key={api_key}&query=New York'

def fetch_data():
  print("Fetching weather data from Weatherstack API...")
  try:
    response = requests.get(api_url)
    # raise an exception for 4XX or 5XX HTTP errors
    response.raise_for_status()
    
    print("API response received successfully.")
    
    return response.json()
  except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    raise

fetch_data()


def mock_fetch_data():
  """
  Simulating the weather data response 
  """
  return {
          "request": {
            "type": "City",
            "query": "Taipei, Taiwan",
            "language": "en",
            "unit": "m"
          },
          "location": {
            "name": "Taipei",
            "country": "Taiwan",
            "region": "Taipei City",
            "lat": "25.0478",
            "lon": "121.5319",
            "timezone_id": "Asia/Taipei",
            "localtime": "2026-02-10 23:00",
            "localtime_epoch": 1770735600,
            "utc_offset": "8.0"
          },
          "current": {
            "observation_time": "11:00 PM",
            "temperature": 18,
            "weather_code": 116,
            "weather_icons": [
              "https://assets.weatherstack.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"
            ],
            "weather_descriptions": [
              "Partly cloudy"
            ],
            "wind_speed": 15,
            "wind_degree": 90,
            "wind_dir": "E",
            "pressure": 1018,
            "precip": 0.5,
            "humidity": 82,
            "cloudcover": 50,
            "feelslike": 17,
            "uv_index": 0,
            "visibility": 8,
            "is_day": "no"
          }
        }