from .models import Intent, ActionParameter

class Session:
    """
    This class represents a conversation session with a user.

    It manages the conversation flow, including:
        - Agent: The agent associated with the session.
        - Context: A list of contexts currently active in the conversation (initially set to ["welcome"]).
        - Input: The user"s latest input text.
        - Intents: All intents associated with the agent.
        - Actions: List of action parameters for the current intent (if applicable).
        - Current Intent: The intent identified for the current user input (or None if not found).
        - Current Action Index: Index of the current action parameter being collected (starts at 1).
        - Total Action Count: Total number of action parameters for the current intent (if applicable).
        - Executing Action: Flag indicating if the session is currently collecting user input for action parameters.
        - Data: Dictionary to store user-provided values for action parameters (keys are parameter names, values are user input).

    The class defines methods for:
        - Starting an action sequence (collecting user input for action parameters).
        - Handling the execution of action sequences.
        - Loading data (response or prompts) and replacing placeholders with collected user input.
        - Identifying the most suitable intent based on active contexts and user input.
        - Updating the context after processing user input.
        - Processing user input and generating a response based on the identified intent and context.
    """
    def __init__(self, agent):
        self.agent = agent
        self.context = []  # Starts with "welcome" context
        self.input = ""
        self.intents = self.agent.intents.all()
        self.actions = None
        self.current_intent = None
        self.current_action = 0
        self.actions_count = 0
        self.executing_action = False
        self.data = {}

    def start_action(self, actions):
        """
        Initiates the process of collecting user input for a sequence of action parameters.

        - Sets flags and counters for action execution.
        - Initializes data dictionary with empty values for required action parameters.
        - Loads and returns prompts (if any) for the first action parameter.
        """
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
        """
        Handles the processing of user input during an action sequence.

        - Stores the user"s input for the current action parameter.
        - Increments the action index or resets if all actions are collected.
        - Updates the execution flag and returns the processed response (potentially with loaded data).
        """
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
        """
        Replaces placeholders in a response (prompts or intent response) with collected user input.

        - Iterates through data keys (action parameter names).
        - Replaces occurrences of each key in the response with the corresponding value from the data dictionary.
        - Returns the processed response with replaced placeholders.
        """
        edit_response = response
        data = list(self.data.keys())
        for i in data:
            edit_response = edit_response.replace(i, self.data[i])
        return edit_response
    
    def get_intent(self):
        """
        Identifies the most suitable intent based on active contexts and user input.

        - Iterates through all intents associated with the agent.
        - Checks if any active context matches an input context of the intent.
        - Handles confirmation intents with context names ending in "Confirm".
        - Additionally checks if any training phrase of the intent matches the user input (lowerCase).
        - Returns the identified intent or None if no match is found.
        """
        for intent in self.intents:
            if any(context in [context.name for context in intent.input_contexts.all()] for context in self.context):
                return intent
            elif any(str(list(context.keys())[0]) + "Confirm" in [context.name for context in intent.input_contexts.all()] for context in self.context):
                if any(text in self.input.lower() for text in intent.training_phrases):
                    return intent
        return None

    def update_context(self, new_context):
        """
        Updates the active contexts in the session based on the provided new contexts.

        - Iterates through existing contexts and decrements their duration.
        - Removes contexts with a duration reaching 0.
        - Appends new contexts with their initial duration to the active context list.
        """
        for context in self.context:
            name = list(context.keys())[0]
            if context[name]["duration"] > 1:
                context[name]["duration"] -= 1
            elif context[name]["duration"] == 1:
                # Se a duração for igual a 1, remove o contexto atual
                self.context.remove(context)
        self.context += [{context.name: {"duration":context.duration, "value":{}}} for context in new_context]

    def process_request(self):
        """
        The main method for processing user input and generating a response.

        - Handles initial conversation flow (identifying the "welcome" intent if no context exists).
        - Identifies the most suitable intent based on active contexts and user input.
        - Initiates action execution if action parameters are defined for the intent.
        - Handles ongoing action sequences if the session is already collecting user input for actions.
        - Updates the context based on the identified intent"s output contexts (if not executing actions).
        - Loads and returns the processed response (intent response or prompts) potentially with replaced placeholders.
        - Returns None if no suitable intent is found.
        """
        if len(self.context) == 0:
            self.current_intent = self.intents.filter(events__icontains="'welcome'").first()
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