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
    
def orc(conversation_id,question):
    client_principal_id = '00000000-0000-0000-0000-000000000000'
    client_principal_name = 'anonymous'

    client_principal = {
        'id': client_principal_id,
        'name': client_principal_name
    }

    # Call orchestrator
    if question:
        orchestrator = Orchestrator(conversation_id)
        result = orchestrator.answer([],question)
        return result.get("answer")
    else:
        return False
    
if __name__ == "__main__":
    print(orc('djsncd','hi'))