import json
import os
import time
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
import functions

class OpenAIClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = functions.create_assistant(self.client)

    def start_conversation(self):
        thread = self.client.beta.threads.create()
        return thread.id

    def send_message(self, thread_id, user_input):
        print(f"send_message: {thread_id} - {user_input}")
        self.client.beta.threads.messages.create(thread_id=thread_id,
                                                 role="user",
                                                 content=user_input)

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
                self.handle_action(run_status, thread_id, run.id)
            time.sleep(1)
            count += 1

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value

    def handle_action(self, run_status, thread_id, run_id):
        for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
            print(f"tool_call: {tool_call.function.name}")
            if tool_call.function.name in ["get_geocode", "get_weather"]:
                arguments = json.loads(tool_call.function.arguments)
                print(f"parametros: {arguments}")
                output = getattr(functions, tool_call.function.name)(**arguments)
                self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                                  run_id=run_id,
                                                                  tool_outputs=[{
                                                                      "tool_call_id": tool_call.id,
                                                                      "output": json.dumps(output)
                                                                  }]
                                                                )

class FlaskApp:
    def __init__(self, test_mode=False):
        self.app = Flask(__name__)
        self.openai_client = OpenAIClient(api_key=os.environ['OPENAI_API_KEY'])
        if test_mode:
          self.setup_routes()

    def run(self):
        self.app.run(host='0.0.0.0', port=8080)

    def setup_routes(self):
        @self.app.route('/start', methods=['GET'])
        def start_conversation():
            thread_id = self.openai_client.start_conversation()
            return jsonify({"thread_id": thread_id})

        @self.app.route('/message', methods=['POST'])
        def message():
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
