from django.contrib import admin
from .models import Agent, Intent, Context, ActionParameter

admin.site.register(Agent)
admin.site.register(Intent)
admin.site.register(ActionParameter)
admin.site.register(Context)
