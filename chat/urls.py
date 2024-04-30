from django.urls import include, path
from .views import *



urlpatterns = [
    path("<str:token>/", ChatbotView.as_view(), name="chatBot"),
]