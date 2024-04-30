from .models import Intent, ActionParameter

class Session:
    def __init__(self, agent):
        self.agent = agent
        self.context = []  # Inicia com 'welcome'
        self.input = ''
        self.intents = self.agent.intents.all()
        self.current_intent = None
        self.executing_action = False
        self.data = {}

    def get_intent(self):
        if ActionParameter.objects.filter(intent=self.current_intent):
            return None
        else:
            for intent in self.intents:
                if any(context in [context.name for context in intent.input_contexts.all()] for context in self.context):
                    return intent
                elif any(str(list(context.keys())[0]) + "Confirm" in [context.name for context in intent.input_contexts.all()] for context in self.context):
                    if any(text in self.input for text in intent.training_phrases):
                        return intent
        return None

    def update_context(self, new_context):
        for context in self.context:
            name = list(context.keys())[0]
            if context[name]['duration'] > 1:
                context[name]['duration'] -= 1
            elif context[name]['duration'] == 1:
                # Se a duração for igual a 1, remove o contexto atual
                self.context.remove(context)
        self.context += [{context.name: {"duration":context.duration, "value":{}}} for context in new_context]

    def process_request(self, request_data):
        if len(self.context) == 0:
            self.current_intent = self.intents.filter(events__icontains='"welcome"').first()
            print(self.current_intent)
        elif not self.executing_action:
            self.current_intent = self.get_intent()
            
        if self.current_intent:
            self.update_context(self.current_intent.output_contexts.all())
            return self.current_intent.response
        return None