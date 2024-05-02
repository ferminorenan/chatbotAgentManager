from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 

from main.models import Project
from .models import Agent
from .response import Session

# Dicionário para armazenar as sessões ativas de cada solicitante
sessions = {}

class ChatbotView(APIView):
    def post(self, request, token):
        try:
            project = Project.objects.get(token=token)
            agent = Agent.objects.get(project=project)
            requester_id = request.META.get('REMOTE_ADDR')  # Obtém o ID do solicitante (neste caso, o IP do cliente)
            
            # Verifica se já existe uma sessão para este solicitante
            if requester_id in sessions:
                session = sessions[requester_id]
            else:
                # Se não existir, cria uma nova sessão para o solicitante
                session = Session(agent)
                sessions[requester_id] = session

            request_data = request.data
            session.input = request_data.get("input","")
            response = session.process_request()
            save_history(requester_id, session, )
            
            if response is None:
                # Se response for None, indica que a sessão deve ser encerrada
                del sessions[requester_id]  # Remove a sessão após o término
                return Response({'response': 'Sessão encerrada.'}, status=status.HTTP_200_OK)
            
            return Response({'response': str(response), 'context': session.context, 'data': session.data}, status=status.HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response({'error': 'Projeto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Agent.DoesNotExist:
            return Response({'error': 'Agente não encontrado para o projeto especificado.'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, token):
        return Response({'response': 'teste'}, status=status.HTTP_200_OK)
