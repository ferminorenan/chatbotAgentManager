from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from main.models import Project
from .models import Session_historic, Message, Agent, Intent, Context

class ChatbotViewTest(APITestCase):

    def setUp(self):
        # Configuração inicial para os testes
        self.project = Project.objects.create(name="Projeto de Teste", token="token_teste")
        self.agent = Agent.objects.create(name="Agente de Teste", project=self.project)
        self.context = Context.objects.create(name='welcomeFollowUp',agent=self.agent)
        self.intent = Intent.objects.create(
            agent=self.agent,
            name="welcome",
            response="Resposta da Intent de teste",
            events=["welcome"],
        )
        self.intent.output_contexts.add(self.context)

    def test_post_chatbot_view(self):
        # Testa o endpoint POST do ChatbotView

        url = reverse('chatBot', kwargs={'token': self.project.token})
        data = {'input': 'Olá, teste'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('context', response.data)
        self.assertIn('data', response.data)

        # Verifica se a sessão histórica foi salva
        self.assertTrue(Session_historic.objects.exists())

        # Verifica se a mensagem do usuário foi salva
        self.assertTrue(Message.objects.filter(sender='user').exists())

        # Verifica se a mensagem do bot foi salva
        self.assertTrue(Message.objects.filter(sender='bot').exists())

    def test_get_chatbot_view(self):
        # Testa o endpoint GET do ChatbotView

        url = reverse('chatBot', kwargs={'token': self.project.token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['response'], 'teste')

class WhatsAppBotViewTest(APITestCase):

    def setUp(self):
        # Configuração inicial para os testes
        self.project = Project.objects.create(name="Projeto de Teste", token="token_teste")
        self.agent = Agent.objects.create(name="Agente de Teste", project=self.project)
        self.context = Context.objects.create(name='welcomeFollowUp',agent=self.agent)
        self.intent = Intent.objects.create(
            agent=self.agent,
            name="welcome",
            response="Resposta da Intent de teste",
            events=["welcome"],
        )
        self.intent.output_contexts.add(self.context)

    def test_post_whatsapp_bot_view(self):
        # Testa o endpoint POST do WhatsAppBotView

        url = reverse('whatsappBot', kwargs={'token': self.project.token})
        data = {'input': 'Olá, teste', 'to': 'whatsapp:+14155238886'}  # Substituir pelo número correto

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('context', response.data)
        self.assertIn('data', response.data)
        self.assertIn('message_sid', response.data)

        # Verifica se a sessão histórica foi salva
        self.assertTrue(Session_historic.objects.exists())
        # Verifica se a mensagem do usuário foi salva
        self.assertTrue(Message.objects.filter(sender='user').exists())
        # Verifica se a mensagem do bot foi salva
        self.assertTrue(Message.objects.filter(sender='bot').exists())

    def test_get_whatsapp_bot_view(self):
        # Testa o endpoint GET do WhatsAppBotView

        url = reverse('whatsappBot', kwargs={'token': self.project.token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['response'], 'teste')
