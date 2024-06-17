from rest_framework.views import APIView  # Importação para views baseadas em classes da API
from rest_framework.response import Response  # Importação para criar respostas HTTP
from rest_framework import status, viewsets  # Importação para lidar com códigos de status HTTP

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from main.models import Project  # Importa o modelo Project do app main
from .models import Session_historic, Message, Agent  # Importa o modelo Agent e outros do app atual
from .response import Session  # Importa a classe Session para lógica de conversa
from .serializers import Session_historic_serializer
from .functions import send_mensage_whatsapp

import json
# Dicionário para armazenar as sessões ativas de cada solicitante
sessions = {}

class ChatbotView(APIView):
    def post(self, request, token):
        """
        Endpoint POST para lidar com interações de chatbot via API.

        - Recupera o projeto e agente associado ao token fornecido.
        - Identifica o solicitante pela sua identificação de IP.
        - Verifica se uma sessão já existe para o solicitante ou cria uma nova.
        - Processa a entrada do usuário e gera uma resposta.
        - Salva a sessão histórica e mensagens trocadas no banco de dados.
        - Retorna a resposta, contexto e dados da sessão.
        """
        try:
            project = Project.objects.get(token=token)  # Recupera o projeto pelo token
            agent = Agent.objects.get(project=project) 
            # Recupera o agente associado ao projeto
            requester_id = request.META.get("REMOTE_ADDR")  # Obtém o endereço IP do solicitante para identificação da sessão

            # Verifica se uma sessão já existe para este solicitante
            if requester_id in sessions:
                session = sessions[requester_id]
            else:
                # Cria uma nova sessão se não existir
                session = Session(agent)
                sessions[requester_id] = session

            session.input = request.data.get("input", "")  # Atualiza a entrada da sessão com a entrada do usuário (ou string vazia se não fornecida)
            response = session.process_request()  # Processa a entrada do usuário e gera uma resposta

            if response is None:
                # Se a resposta for None, encerra a sessão
                Session_historic.objects.filter(agent=agent, requester_ip=requester_id, closed=False).update(closed=True)
                del sessions[requester_id]  # Remove a sessão do dicionário de sessões ativas
                return Response({"response": "Sessão encerrada."}, status=status.HTTP_200_OK)

            defaults = {
                    "context": session.context,
                    "input": session.input,
                    "current_intent": session.current_intent,
                    "executing_action": session.executing_action,
                    "data": session.data,
                    "closed": False,
                    "agent": agent,
                    "requester_ip": requester_id,
                }
            # Tenta atualizar ou criar o histórico da sessão
            session_historic, created = Session_historic.objects.update_or_create(
                agent=agent,
                requester_ip=requester_id,
                closed=False,
                defaults=defaults
            )
            if not created:
                defaults["agent"] = agent.pk
                defaults["current_intent"] = session.current_intent.pk
                # Se a intent atual tiver a ação 'welcome', fecha todos os históricos abertos e cria um novo
                if session.current_intent.events and 'welcome' in session.current_intent.events:
                    Session_historic.objects.filter(agent=agent, requester_ip=requester_id, closed=False).update(closed=True)
                    session_historic = Session_historic.objects.create(**defaults)
                # Caso contrário, atualiza o histórico existente
                serializer = Session_historic_serializer(session_historic, data=defaults)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print("error", serializer.errors)

            # Salva a mensagem do usuário no banco de dados
            user_message = Message(
                session=session_historic,
                content=request.data.get("input", ""),
                sender="user",
            )
            user_message.save()

            # Salva a resposta do chatbot como mensagem no banco de dados
            bot_message = Message(
                session=session_historic,
                content=response,
                sender="bot",
            )
            bot_message.save()

            # Retorna a resposta, contexto e dados da sessão
            return Response({"response": str(response), "context": session.context, "data": session.data}, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        except Agent.DoesNotExist:
            return Response({"error": "Agente não encontrado para o projeto especificado."}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, token):
        """
        Endpoint GET de teste para o ChatbotView.

        - Retorna uma resposta de teste para solicitações GET.
        """
        return Response({"response": "teste"}, status=status.HTTP_200_OK)


class WhatsAppBotView(APIView):
    def post(self, request, token):
        """
        Endpoint POST para lidar com interações via WhatsApp.

        - Recupera o projeto e agente associado ao token fornecido.
        - Identifica o solicitante pela sua identificação de IP.
        - Verifica se uma sessão já existe para este solicitante ou cria uma nova.
        - Processa a entrada do usuário e gera uma resposta.
        - Envia a resposta via WhatsApp usando o Twilio.
        - Salva a sessão histórica e mensagens trocadas no banco de dados.
        - Retorna a resposta, contexto, dados da sessão e o SID da mensagem enviada.
        """
        try:
            project = Project.objects.get(token=token)  # Recupera o projeto pelo token
            agent = Agent.objects.get(project=project)  # Recupera o agente associado ao projeto
            data = json.loads(request.body.decode('utf-8'))
            mensagem = data['entry'][0]['changes'][0]['value']['messages'][-1]
            requester_id = mensagem["from"] # Obtém o numero do solicitante para identificação da sessão
            # Verifica se o agente tem configurações para integração com o WhatsApp via Twilio
            if not agent.whatsapp_business_api_token or not agent.whatsapp_business_phone_number:
                return Response({"error": "Agente não possui integração com WhatsApp configurada."}, status=status.HTTP_400_BAD_REQUEST)


            # Verifica se uma sessão já existe para este solicitante
            if requester_id in sessions:
                session = sessions[requester_id]
            else:
                # Cria uma nova sessão se não existir
                session = Session(agent)
                sessions[requester_id] = session

            session.input = mensagem['text']['body']  # Atualiza a entrada da sessão com a entrada do usuário (ou string vazia se não fornecida)
            response = session.process_request()  # Processa a entrada do usuário e gera uma resposta

            if response is None:
                # Se a resposta for None, encerra a sessão
                Session_historic.objects.filter(agent=agent, requester_ip=requester_id, closed=False).update(closed=True)
                del sessions[requester_id]  # Remove a sessão do dicionário de sessões ativas
                return Response({"response": "Sessão encerrada."}, status=status.HTTP_200_OK)

            result = send_mensage_whatsapp(agent.whatsapp_business_api_token, agent.whatsapp_business_phone_number, requester_id, str(response))
            if 'error' in result:
                return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
            
            defaults = {
                    "context": session.context,
                    "input": session.input,
                    "current_intent": session.current_intent,
                    "executing_action": session.executing_action,
                    "data": session.data,
                    "closed": False,
                    "agent": agent,
                    "requester_ip": requester_id,
                }
            # Tenta atualizar ou criar o histórico da sessão
            session_historic, created = Session_historic.objects.update_or_create(
                agent=agent,
                requester_ip=requester_id,
                closed=False,
                defaults=defaults
            )
            if not created:
                defaults["agent"] = agent.pk
                defaults["current_intent"] = session.current_intent.pk
                # Se a intent atual tiver a ação 'welcome', fecha todos os históricos abertos e cria um novo
                if session.current_intent.events and 'welcome' in session.current_intent.events:
                    Session_historic.objects.filter(agent=agent, requester_ip=requester_id, closed=False).update(closed=True)
                    session_historic = Session_historic.objects.create(**defaults)
                # Caso contrário, atualiza o histórico existente
                serializer = Session_historic_serializer(session_historic, data=defaults)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print("error", serializer.errors)

            # Salva a mensagem do usuário no banco de dados
            user_message = Message(
                session=session_historic,
                content=request.data.get("input", ""),
                sender="user",
            )
            user_message.save()

            # Salva a resposta do chatbot como mensagem no banco de dados
            bot_message = Message(
                session=session_historic,
                content=response,
                sender="bot",
            )
            bot_message.save()

            # Retorna a resposta, contexto, dados da sessão e o SID da mensagem enviada
            return Response({
                "response": "mensagem enviada com sucesso.",
            }, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        except Agent.DoesNotExist:
            return Response({"error": "Agente não encontrado para o projeto especificado."}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, token):
        """
        Endpoint GET de teste para o WhatsAppBotView.

        - Retorna uma resposta de teste para solicitações GET.
        """
        return Response({"response": "teste"}, status=status.HTTP_200_OK)

class Agent_viewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]