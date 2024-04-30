from django.contrib import admin
from .models import Agent, Intent, Context, ActionParameter

class IntentAdmin(admin.ModelAdmin):
    exclude = ('action_parameters',)

admin.site.register(Agent)
admin.site.register(Intent, IntentAdmin)
admin.site.register(ActionParameter)
admin.site.register(Context)
