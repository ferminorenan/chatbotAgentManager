from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from .models import Context, Intent, Agent, ActionParameter, ConversationHistory
from nested_inline.admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline

class ActionParameterInline(NestedTabularInline):
    model = ActionParameter
    extra = 0
    classes = ('collapse', )

class ContextInline(NestedTabularInline):
    model = Context
    extra = 0
    classes = ('collapse', )
class IntentInline(NestedTabularInline):
    model = Intent
    extra = 0
    inlines = [ActionParameterInline]
    classes = ('collapse', )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "input_contexts" or db_field.name == "output_contexts":
            try:
                agent_id = request.path.split('/')[4]
                agent = Agent.objects.get(pk=agent_id)
                kwargs["queryset"] = Context.objects.filter(agent=agent)
            except IndexError:
                pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(Agent)
class AgentAdmin(NestedModelAdmin):
    list_display = ["name", "project", "default_language", "default_timezone", "project_test_url"]

    def has_add_permission(self, request):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(project__user=request.user)

    def project_test_url(self, obj):
        if obj.project:
            url = reverse('chatBot', kwargs={'token': obj.project.token})
            return format_html('<a href="{}">{}</a>', url, url)
        return "-"
    project_test_url.short_description = "URL de Teste do Agente"
    

    fieldsets = (
        (None, {"fields": ("project", "name", "default_language", "default_timezone")}),
    )
    readonly_fields = ["project_test_url"]
    inlines = [IntentInline, ContextInline]