import json
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

class Api:

    #las funciones que luego hay que codificar y se corresponden con las tool calls, son atributos de clase para indicar las funciones que ofrece esta api
    functions_list = ["get_geocode", "get_weather"]

    def __init__(self):
        # Carga las variables de entorno desde .env
        load_dotenv()

        self.mapbox_api_key = os.environ['MAPBOX_API_KEY']
        self.openweather_api_key = os.environ['OPENWEATHER_API_KEY']

    # Get Geocoding
    def get_geocode(self, search_text):
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json?access_token={self.mapbox_api_key}"
        print(f"log: {url}")
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
            #place = data['features'][0]['place_name']
            #location = data['features'][0]['center']    
            #return location[1], location[0]
            return data
        else:
            print(f"Error: {response.text}")
            return None

    # Get Weather
    def get_weather(self, lat, lon, units="metric"):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={self.openweather_api_key}"
        print(f"log: {url}")
        response = requests.get(url=url)
        if response.status_code == 200:
            print("Successfully.")
            return response.json()
        else:
            print(f"Error: {response.text}")
            return None