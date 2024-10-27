import json
from config import (
    OPENAI_GPT4_DEPLOYMENT,MAX_ERROR_RUN,
    MAX_RUN_PER_QUESTION,client
)
from utils import check_args


        
class Agent():
    def __init__(self, persona,functions_spec, functions_list, name=None, init_message=None, engine =OPENAI_GPT4_DEPLOYMENT):
        if init_message is not None:
            init_hist =[{"role":"system", "content":persona}, {"role":"assistant", "content":init_message}]
        else:
            init_hist =[{"role":"system", "content":persona}]

        self.conversation =  init_hist
        self.persona = persona
        self.engine = engine
        self.persona ="coder"
        self.name= name

        self.functions_spec = functions_spec
        self.functions_list= functions_list
  
    def run(self, user_input, conversation=None, stream = False, ):
        if user_input is None: #if no input return init message
            return self.conversation, self.conversation[1]["content"]
        if conversation is not None: #if no history return init message
            self.conversation = conversation

        self.conversation.append({"role": "user", "content": user_input, "name": "James"})
        execution_error_count=0
        code = ""
        response_message = None
        data ={}
        execution_context={}
        run_count =0
        while True:
            if run_count >= MAX_RUN_PER_QUESTION:
                response_message= {"role": "assistant", "content": "I am unable to answer this question at the moment, please ask another question."}
                break
            if execution_error_count >= MAX_ERROR_RUN:
                print(f"resetting history due to too many errors ({execution_error_count} errors) in the code execution")
                execution_error_count=0
            response = client.chat.completions.create(
                model=self.engine, # The deployment name you chose when you deployed the GPT-35-turbo or GPT-4 model.
                messages=self.conversation,
                tools=self.functions_spec,
                tool_choice='auto',
                temperature=0.2,
            )

            run_count+=1
            response_message = response.choices[0].message
            if response_message.content is None:
                response_message.content = ""
            tool_calls = response_message.tool_calls
            
            # Step 2: check if GPT wanted to call a function
            if  tool_calls:
                self.conversation.append(response_message) 
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
           
                    # verify function exists
                    if function_name not in self.functions_list:
                        # raise Exception("Function " + function_name + " does not exist")
                        print(("Function " + function_name + " does not exist, retrying"))
                        self.conversation.pop()
                        break
                    function_to_call = self.functions_list[function_name]
                    
                    # verify function has correct number of arguments
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        print(e)
                        self.conversation.pop()
                        break
                    if function_name == "execute_python_code":
                        function_args["execution_context"] = execution_context

                    if check_args(function_to_call, function_args) is False:
                        self.conversation.pop()
                        break
                    if function_name == "execute_python_code":
                        execution_context, function_response = function_to_call(**function_args)
                        # if "data" in st.session_state:
                        #     data[tool_call.id] = st.session_state['data']
                        if "error" in function_response:
                            execution_error_count+=1
                        else:
                            code = function_args["python_code"]


                    else:
                        print("#####",function_name,function_args)
                        function_response = str(function_to_call(**function_args))
                                     
                    # print("Output of function call:")
                    # print("length of function_response", len(function_response))
                    print()
                    if function_name == "message_user" or function_name =="message_team": #special case when coder finished the code execution and ready to respond to user or the coder needs to clarify with context preparer
                        return function_response

                
                    self.conversation.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )  # extend conversation with function response
                    

                continue
            else:
                # print('no function call')
                break #if no function call break out of loop as this indicates that the agent finished the research and is ready to respond to the user

        if not stream:
            self.conversation.append(response_message)
            if type(response_message) is dict:
                assistant_response = response_message.get('content')
            else:
                assistant_response = response_message.dict().get('content')
            # conversation.append({"role": "assistant", "content": assistant_response})

        else:
            assistant_response = response_message

        return stream,code, self.conversation, assistant_response, data