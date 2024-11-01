from orchestration.orchestrator import Orchestrator
from uuid import uuid4

class Smart_Agent():
    """
    """

    def __init__(self):
        init_hist =[]
        self.conversation =  init_hist
        self.conversation_id = str(uuid4())
        self.orchestrator = Orchestrator(self.conversation_id)


    # @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def run(self, user_input, conversation=None, stream = False, ):
        
        self.conversation.append({"role": "user", "content": user_input})
            
        code = ""
        data ={}
        
        assistant_response = self.orchestrator.answer(self.conversation,user_input).get('answer')
        return stream,code, self.conversation, assistant_response, data