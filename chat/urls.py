from django.urls import include, path
from .views import *



urlpatterns = [
    path("api/<str:token>/", ChatbotView.as_view(), name="chatBot"),
    path('api/whatsapp/<str:token>/', WhatsAppBotView.as_view(), name='whatsappBot'),
]