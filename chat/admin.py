from django.contrib import admin
from django.http import HttpRequest
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
    list_display = ["name", "project", "default_language", "default_timezone"]  

    def has_add_permission(self, request):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(project__user=request.user)
    # Tornar obrigatório o campo project
    fieldsets = (
        (None, {"fields": ("project", "name", "default_language", "default_timezone")}),
    )
    inlines = [IntentInline, ContextInline]