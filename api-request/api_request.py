import requests
from dotenv import load_dotenv


load_dotenv('./.env')

api_url = ''

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
  return {}