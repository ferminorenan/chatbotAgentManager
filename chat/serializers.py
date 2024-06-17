from rest_framework import serializers
from .models import *

class Session_historic_serializer(serializers.ModelSerializer):
    class Meta:
        model = Session_historic
        fields = "__all__"