from django.test import TestCase
from django.urls import reverse


class ChatbotEndpointTests(TestCase):
    def test_chatbot_endpoint_returns_answer(self):
        response = self.client.post(
            reverse('chatbot-query'),
            {'question': 'What content is available?'},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('answer', response.json())
        self.assertTrue(response.json()['answer'])
