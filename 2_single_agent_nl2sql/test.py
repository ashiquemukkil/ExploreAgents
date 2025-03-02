from agent import Agent
from prompt import CODER_FUNCTIONS_SPEC,CODER
from utils import CODER_AVAILABLE_FUNCTIONS
agent = Agent(persona=CODER,functions_list=CODER_AVAILABLE_FUNCTIONS, functions_spec=CODER_FUNCTIONS_SPEC, init_message="Hello, I am your AI Analytic Assistant, what question do you have？")

if __name__ == "__main__":
    user_input = "give top 5 product with price"
    stream_out, code, history, agent_response,data = agent.run(user_input=user_input, conversation=[], stream=False)
    print(agent_response)