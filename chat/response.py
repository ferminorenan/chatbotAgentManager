from .models import Intent

class Session:
    def __init__(self, agent):
        self.agent = agent
        self.context = 'welcome'  # Inicia com 'welcome'
        self.input = ''
        self.intents = Intent.objects.filter(agents=self.agent)
    
    def get_response_from_events(self):
        try:
            if self.intents:
                for intent in self.intents:
                    if {"event": self.context} in intent.events:
                        # Se encontrarmos a intenção, retornamos a resposta correspondente
                        #self.context = 
                        self.context = [{context.name: context.duration} for context in intent.output_contexts.all()]
                        return intent.response
                return 'Desculpe, não consegui encontrar uma resposta para este evento.'
            else:
                # Se não houver uma intenção com o evento de boas-vindas no agente selecionado, retornamos uma mensagem padrão
                return 'Desculpe, não consegui encontrar uma intenção para este agente.'
        except Exception as e:
            # Em caso de qualquer erro, retornamos uma mensagem genérica
            print(e)
            return 'Ocorreu um erro ao processar sua solicitação.'
        
    def get_response_from_context(self):
        try:
            if self.intents:
                for intent in self.intents:
                    if any(context in [context.name for context in intent.input_contexts.all()] for context in self.context):
                        self.update_context_duration(self.context, intent.output_contexts.all())
                        return intent.response
                    else:
                        if any(str(list(context.keys())[0]) + "Confirm" in [context.name for context in intent.input_contexts.all()] for context in self.context):
                            if any(text in self.input for text in intent.training_phrases):
                                self.update_context_duration(self.context, intent.output_contexts.all())
                                return intent.response

            else:
                # Se não houver uma intenção com o evento de boas-vindas no agente selecionado, retornamos uma mensagem padrão
                return 'Desculpe, não consegui encontrar uma intenção para este agente.'
        except Exception as e:
            # Em caso de qualquer erro, retornamos uma mensagem genérica
            print(e)
            return 'Ocorreu um erro ao processar sua solicitação.'
    
    def update_context_duration(self, previous_context, new_context):
        for context in self.context:
            name = list(context.keys())[0]
            if name in [list(prev.keys())[0] for prev in previous_context]:
                # Se o contexto estiver presente no contexto anterior, reduz a duração
                index = [list(prev.keys())[0] for prev in previous_context].index(name)
                previous_duration = list(previous_context[index].values())[0]
                if context[name] > 1:
                    context[name] -= 1
                elif context[name] == 1:
                    # Se a duração for igual a 1, remove o contexto atual
                    self.context.remove(context)
        self.context += [{context.name: context.duration} for context in new_context]

    def process_request(self, request_data):
        if self.context == 'welcome':
            return self.get_response_from_events()
        if 'end_session' in request_data:
            return None  # Se o comando de encerrar for recebido, retorna None para indicar fim da sessão
        return self.get_response_from_context()