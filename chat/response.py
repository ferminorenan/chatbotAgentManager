from .models import Intent, ActionParameter

class Session:
    def __init__(self, agent):
        self.agent = agent
        self.context = []  # Inicia com 'welcome'
        self.input = ''
        self.intents = self.agent.intents.all()
        self.actions = None
        self.current_intent = None
        self.current_action = 0
        self.actions_count = 0
        self.executing_action = False
        self.data = {}

    def start_action(self, actions):
        self.executing_action = True
        self.current_action = 1
        self.actions = actions
        self.actions_count = len(actions)
        for action in actions:
            if action.required:
                self.data = {**self.data,
                                action.value: ""
                            }
        return self.load_data(actions.filter(order=1).first().prompts)

    def executing_actions(self):
        action = self.actions.filter(order=self.current_action).first()
        self.data[action.value] = self.input
        if self.current_action > self.actions_count:
            self.current_action += 1
        else:
            self.current_action = 1
            self.actions_count = 0
            self.executing_action = False
        return self.load_data(self.current_intent.response)

    def load_data(self, response):
        edit_response = response
        data = list(self.data.keys())
        for i in data:
            edit_response = edit_response.replace(i, self.data[i])
        return edit_response
    
    def get_intent(self):
        for intent in self.intents:
            if any(context in [context.name for context in intent.input_contexts.all()] for context in self.context):
                return intent
            elif any(str(list(context.keys())[0]) + "Confirm" in [context.name for context in intent.input_contexts.all()] for context in self.context):
                if any(text in self.input.lower() for text in intent.training_phrases):
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

    def process_request(self):
        if len(self.context) == 0:
            self.current_intent = self.intents.filter(events__icontains='"welcome"').first()
        elif not self.executing_action:
            self.current_intent = self.get_intent()
            if ActionParameter.objects.filter(intent=self.current_intent):
                return self.start_action(ActionParameter.objects.filter(intent=self.current_intent))
        elif self.executing_action:
            return self.executing_actions()

        if self.current_intent and not self.executing_action:
            self.update_context(self.current_intent.output_contexts.all())
            return self.load_data(self.current_intent.response)
        
        return None