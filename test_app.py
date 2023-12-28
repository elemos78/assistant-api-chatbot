import unittest
import json
import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.FlaskApp(test_mode=True).app
        self.app.testing = True
        self.client = self.app.test_client()

    def test_lat_long_barcelona(self):
        # Iniciar conversación
        start_response = self.client.get('/start')
        print(start_response)
        thread_id = json.loads(start_response.data)['thread_id']

        # Enviar mensaje
        response = self.client.post('/prompt', json={
            'thread_id': thread_id,
            'message': '¿Cuál es la latitud y longitud de Barcelona?'
        })
        data = json.loads(response.data)
        self.assertIn('latitud', data['response'].lower())
        self.assertIn('longitud', data['response'].lower())

    def test_weather_barcelona(self):
        # Iniciar conversación
        start_response = self.client.get('/start')
        thread_id = json.loads(start_response.data)['thread_id']

        # Enviar mensaje
        response = self.client.post('/prompt', json={
            'thread_id': thread_id,
            'message': '¿Cuál es el clima de Barcelona?'
        })
        data = json.loads(response.data)
        self.assertIn('clima', data['response'].lower())
        self.assertIn('barcelona', data['response'].lower())

if __name__ == '__main__':
    unittest.main()
