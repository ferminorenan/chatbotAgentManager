from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import LANGUAGE_CHOICES, TIMEZONE_CHOICES, PARAMETER_CHOICES
from main.models import Project

class Agent(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    default_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, null=True, blank=True)
    default_timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, null=True, blank=True)
    whatsapp_business_api_token = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_business_phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Agent)
def create_welcome_intent(sender, instance, created, **kwargs):
    if created:
        welcome_context = Context.objects.create(
            agent = instance,
            name='welcomeFollowUp',
        )
        welcome_intent = Intent.objects.create(
            agent=instance,
            name="welcome",
            response="Olá! Bem-vindo ao nosso serviço de chat.",
            events=["welcome"]
        )
        welcome_intent.output_contexts.add(welcome_context)
        
class Context(models.Model):
    agent = models.ForeignKey(Agent, related_name="agent_context", blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=False, blank=False)
    value = models.CharField(max_length=100, null=True, blank=True)
    duration = models.IntegerField(default=1) 
    def __str__(self):
        return self.name

class Webhook(models.Model):
    agent = models.OneToOneField(Agent, related_name="webhook", on_delete=models.CASCADE)
    url = models.URLField(max_length=200, null=False, blank=False)
    base_auth_name = models.CharField(max_length=100, null=True, blank=True)
    base_auth_password = models.CharField(max_length=100, null=True, blank=True)
    headers = models.JSONField(null=True, blank=True)
    in_line = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Webhook for {self.agent.name}"
    
class Intent(models.Model):
    agent = models.ForeignKey(Agent, related_name="agent_intent", blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=False, blank=False)
    input_contexts = models.ManyToManyField(Context, related_name="intents_input", blank=True)
    output_contexts = models.ManyToManyField(Context, related_name="intents_output", blank=True)
    events = models.JSONField(null=True, blank=True)
    training_phrases = models.JSONField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    fulfillment = models.ForeignKey(Webhook, related_name="intents_fulfillment", blank=True, null=True, on_delete=models.SET_NULL)
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

class Session_historic(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    requester_ip = models.CharField(max_length=100)
    context = models.JSONField(default=list)
    input = models.TextField(blank=True)
    current_intent = models.ForeignKey(Intent, on_delete=models.SET_NULL, null=True, blank=True)
    executing_action = models.BooleanField(default=False)
    data = models.JSONField(default=dict)
    closed = models.BooleanField(default=False)
    
class Message(models.Model):
    session = models.ForeignKey(Session_historic, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sender = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)