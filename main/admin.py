from django.contrib import admin
from .models import *
from chat.models import Agent

class AgentInline(admin.TabularInline):
    model = Agent
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [AgentInline,]