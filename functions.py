import json
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts import assistant_instructions

# Carga las variables de entorno desde .env
load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MAPBOX_API_KEY = os.environ['MAPBOX_API_KEY']
OPENWEATHER_API_KEY = os.environ['OPENWEATHER_API_KEY']

# Init OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Get Geocoding
def get_geocode(search_text):
  url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json?access_token={MAPBOX_API_KEY}"
  print(f"log: {url}")
  response = requests.get(url=url)
  if response.status_code == 200:
    data = response.json()
    place = data['features'][0]['place_name']
    location = data['features'][0]['center']    
    return location[1], location[0]
  else:
    print(f"Error: {response.text}")

# Get Weather
def get_weather(lat, lon, units="metric"):
  url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={OPENWEATHER_API_KEY}"
  print(f"log: {url}")
  response = requests.get(url=url)
  if response.status_code == 200:
    print("Successfully.")
    return response.json()
  else:
    print(f"Error: {response.text}")

# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
  else:
    assistant = client.beta.assistants.create(
        instructions=assistant_instructions,
        model="gpt-3.5-turbo-1106",
        tools=[
            #{
            #    "type": "retrieval"
            #},
            {
                "type": "function",
                "function": {
                    "name": "get_geocode",
                    "description": "Determina la latitud y longitud",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_text": {
                                "type": "string",
                                "description": "Indica la ciudad"
                            }
                        },
                        "required": [
                        "search_text"
                        ]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Determina el clima para una latitud y longitud",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lat": {
                                "type": "string",
                                "description": "latitud"
                            },
                            "lon": {
                                "type": "string",
                                "description": "longitud"
                            },
                            "units": {
                                "type": "string",
                                "enum": [
                                "metric",
                                "imperial"
                                ]
                            }
                        },
                        "required": [
                            "lat",
                            "lon"
                        ]
                    }
                }
            }
        ]#,
        #file_ids=[file.id]
        )

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
    assistant_id = assistant.id

  return assistant_id
