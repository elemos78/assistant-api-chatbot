import json
import os
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from functions import Api

class OpenAIClient:
    def __init__(self, api_key):
        self.assistant_file_path = 'assistant.json'
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = self.create_assistant(self.client)
        self.api_client = Api()

    def log_message(self, thread_id, message):
        with open(f"{thread_id}.log", "a") as log_file:
            log_file.write(message + "\n\n")

    def start_conversation(self):
        thread = self.client.beta.threads.create()
        self.log_message(thread.id, "Iniciando conversación")
        return thread.id

    def send_message(self, thread_id, user_input):        
        self.client.beta.threads.messages.create(thread_id=thread_id,
                                                 role="user",
                                                 content=user_input)
        self.log_message(thread_id, f"Usuario: {user_input}")

    def get_response(self, thread_id):
        print(f"get_response: {thread_id}")
        run = self.client.beta.threads.runs.create(thread_id=thread_id,
                                                   assistant_id=self.assistant_id)
        count = 0
        
        while True and count<=20:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                                run_id=run.id)
            print(f"run_status: {run_status}")
            
            if run_status.status == 'completed':
                break
            elif run_status.status == 'requires_action':
                self.exec_tool_calls(run_status, thread_id, run.id)
            time.sleep(1)
            count += 1

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        self.log_message(thread_id, f"Asistente: {messages.data[0].content[0].text.value}")
        return messages.data[0].content[0].text.value

    def exec_tool_calls(self, run_status, thread_id, run_id):
        for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
            print(f"tool_call: {tool_call.function.name}")
            if tool_call.function.name in self.api_client.functions_list:
                arguments = json.loads(tool_call.function.arguments)
                print(f"parametros: {arguments}")
                output = getattr(self.api_client, tool_call.function.name)(**arguments)
                self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                                  run_id=run_id,
                                                                  tool_outputs=[{
                                                                      "tool_call_id": tool_call.id,
                                                                      "output": json.dumps(output)
                                                                  }]
                                                                )

    # Create or load assistant
    def create_assistant(self, client):        
        if os.path.exists(self.assistant_file_path):
            with open(self.assistant_file_path, 'r') as file:
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

class FlaskApp:
    def __init__(self, test_mode=False):
        load_dotenv()
        self.app = Flask(__name__)
        self.openai_client = OpenAIClient(api_key=os.environ['OPENAI_API_KEY'])        
        if test_mode:
          self.setup_routes()

    def run(self):
        port = int(os.environ.get('PORT', 8080))
        self.app.run(host='0.0.0.0', port=port)

    def setup_routes(self):
        @self.app.route('/start', methods=['GET'])
        def start_conversation():
            thread_id = self.openai_client.start_conversation()
            return jsonify({"thread_id": thread_id})

        @self.app.route('/prompt', methods=['POST'])
        def prompt():
            data = request.json
            thread_id = data.get('thread_id')
            user_input = data.get('message', '')
            if not thread_id:
                return jsonify({"error": "Missing thread_id"}), 400

            self.openai_client.send_message(thread_id, user_input)
            response = self.openai_client.get_response(thread_id)
            return jsonify({"response": response})


if __name__ == '__main__':
    flask_app = FlaskApp()
    flask_app.setup_routes()
    flask_app.run()
