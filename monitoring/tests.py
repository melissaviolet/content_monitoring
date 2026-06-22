from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse


class AnalysePageTests(TestCase):
    def test_analyse_page_is_accessible(self):
        response = self.client.get(reverse('analyse'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Analyse')


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

    @patch('monitoring.views.build_chain')
    @patch('monitoring.views.get_context')
    def test_chatbot_endpoint_uses_context_pipeline(self, mock_get_context, mock_build_chain):
        mock_get_context.return_value = 'Relevant article context'
        mock_chain = Mock()
        mock_chain.invoke.return_value = Mock(content='Answer from context pipeline')
        mock_build_chain.return_value = mock_chain

        response = self.client.post(
            reverse('chatbot-query'),
            {'question': 'What about AI?'},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['answer'], 'Answer from context pipeline')
        mock_get_context.assert_called_once_with('What about AI?')
        mock_chain.invoke.assert_called_once()
