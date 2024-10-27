import asyncio
from orchestration import Orchestrator
from uuid import uuid4

def orc(conversation_id,question):
    client_principal_id = '00000000-0000-0000-0000-000000000000'
    client_principal_name = 'anonymous'

    client_principal = {
        'id': client_principal_id,
        'name': client_principal_name
    }

    # Call orchestrator
    if question:
        orchestrator = Orchestrator(conversation_id, client_principal)
        result = asyncio.run(orchestrator.answer(question))
        return result.get("answer")
    else:
        return False
    
class Smart_Agent():
    """
    """

    def __init__(self):
        init_hist =[]
        self.conversation =  init_hist
        self.conversation_id = str(uuid4())


    # @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def run(self, user_input, conversation=None, stream = False, ):
        
        self.conversation.append({"role": "user", "content": user_input})
            
        code = ""
        data ={}
        
        assistant_response = orc(self.conversation_id,user_input)

        return stream,code, self.conversation, assistant_response, data