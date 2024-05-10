from django.db import models
from .utils import LANGUAGE_CHOICES, TIMEZONE_CHOICES, PARAMETER_CHOICES
from main.models import Project

class Agent(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    default_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, null=True, blank=True)
    default_timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, null=True, blank=True)
    def __str__(self):
        return self.name
    
class Context(models.Model):
    agent = models.ForeignKey(Agent, related_name="agent_context", blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=False, blank=False)
    value = models.CharField(max_length=100, null=True, blank=True)
    duration = models.IntegerField(default=1) 
    def __str__(self):
        return self.name
    
class Intent(models.Model):
    agent = models.ForeignKey(Agent, related_name="agent_intent", blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=False, blank=False)
    input_contexts = models.ManyToManyField(Context, related_name="intents_input", blank=True)
    output_contexts = models.ManyToManyField(Context, related_name="intents_output", blank=True)
    events = models.JSONField(null=True, blank=True)
    training_phrases = models.JSONField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name
    
class ActionParameter(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name="action_parameters_set")
    order = models.IntegerField(default=1)
    required = models.BooleanField(default=False)
    parameter_name = models.CharField(max_length=100)
    entity = models.CharField(max_length=100, choices=PARAMETER_CHOICES)
    value = models.CharField(max_length=100)
    is_list = models.BooleanField(default=False)
    prompts = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.parameter_name} - {self.intent.name}"
    
class ConversationHistory(models.Model):
    session = models.CharField(max_length=20, null=False, blank=False)
    conversasion = models.JSONField()
    update_date = models.DateTimeField()
    closed = models.BooleanField(default=False)
