from rest_framework.views import APIView  # Import for class-based API views
from rest_framework.response import Response  # Import for crafting HTTP responses
from rest_framework import status  # Import for handling HTTP status codes

from main.models import Project  # Import the Project model from the main app
from .models import Agent  # Import the Agent model from the current app
from .response import Session  # Import the Session class for handling conversation logic


# Dicionário para armazenar as sessões ativas de cada solicitante (Dictionary to store active sessions for each requester)
sessions = {}

class ChatbotView(APIView):
    """
    This class-based APIView handles chatbot interactions.
    The view supports two HTTP methods: POST and GET.
    """
    def post(self, request, token):
        """
        Handles POST requests to the chatbot endpoint.

        This method expects a project token in the URL and a JSON request body with an optional "input" field.
        It retrieves the corresponding Project and Agent objects and checks if a session already exists for the requester"s IP address.
        If a session exists, it updates the session"s input with the provided text. If not, a new session is created for the agent.
        The process_request() method of the Session object is then called to handle the user"s input and generate a response.

        The response from the session can be:
            - Textual response: returned directly with context and data from the session.
            - None: indicating the session should be terminated, in which case the session is removed, and a "Sessão encerrada" message is returned.

        Error handling is included for cases where the Project or Agent is not found.
        """
        try:
            project = Project.objects.get(token=token)  # Retrieve project by token
            agent = Agent.objects.get(project=project)  # Retrieve agent associated with the project
            requester_id = request.META.get("REMOTE_ADDR")  # Get requester"s IP address for session identification
            # Check if a session already exists for this requester
            if requester_id in sessions:
                session = sessions[requester_id]
            else:
                # Create a new session if one doesn"t exist
                session = Session(agent)
                sessions[requester_id] = session
            session.input = request.data.get("input", "")  # Update session input with user input (or empty string if not provided)
            response = session.process_request()  # Process the user"s input and generate a response
            if response is None:
                # If response is None, terminate the session
                del sessions[requester_id]  # Remove the session from the active sessions dictionary
                return Response({"response": "Sessão encerrada."}, status=status.HTTP_200_OK)
            # Return the response, context, and data from the session
            return Response({"response": str(response), "context": session.context, "data": session.data}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Agent.DoesNotExist:
            return Response({"error": "Agente não encontrado para o projeto especificado."}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, token):
        """
        Handles GET requests to the chatbot endpoint.

        This method currently returns a simple "teste" response with a 200 OK status code. 
        You can modify this method to handle specific GET requests as needed.
        """
        return Response({"response": "teste"}, status=status.HTTP_200_OK)
