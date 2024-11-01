import streamlit as st
from orch import Smart_Agent

st.set_page_config(layout="wide",page_title="Smart Analytic Copilot Demo Application using LLM")
styl = f"""
<style>
    .stTextInput {{
      position: fixed;
      bottom: 3rem;
    }}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)


MAX_HIST= 3
# Sidebar contents
with st.sidebar:

    st.title('Analytic AI Copilot')
    st.markdown('''
    ''')
    st.checkbox("Show AI Assistant's internal thought process", key='show_internal_thoughts', value=False)
    st.checkbox("Use GPT-4-vision to comment on graph", key='use_gpt4v', value=False)

   
    if st.button('Clear Chat'):

        if 'history' in st.session_state:
            st.session_state['history'] = []
        if 'display_data' in st.session_state:
            st.session_state['display_data'] = {}


    st.markdown("""
                
### Sample Questions:  
1. What were the total sales for each year available in the database?
2. Who are the top 5 customers by order volume, and what is the total number of orders for each?
3. What are the top 10 most popular products based on quantity sold?
4. What are the total sales broken down by country?
                


          """)
    st.write('')
    st.write('')
    st.write('')

    st.markdown('#### Created by James N., 2024')
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'input' not in st.session_state:
        st.session_state['input'] = ""
    if 'display_data' not in st.session_state:
        st.session_state['display_data'] = {}
    if 'question_count' not in st.session_state:
        st.session_state['question_count'] = 0
    if 'solution_provided' not in st.session_state:
        st.session_state['solution_provided'] = False

    if 'agent' not in st.session_state:
        st.session_state['agent'] = Smart_Agent()

agent = st.session_state['agent']      
user_input= st.chat_input("You:")
## Conditional display of AI generated responses as a function of user provided prompts
history = st.session_state['history']
display_data = st.session_state['display_data']
question_count=st.session_state['question_count']
# print("new round-----------------------------------")
# print("question_count: ", question_count)

if len(history) > 0:
    #purging history
    removal_indices =[]
    idx=0
    running_question_count=0
    start_counting=False # flag to start including history items in the removal_indices list
    for message in history:
        idx += 1
        message = dict(message)
        print("role: ", message.get("role"), "name: ", message.get("name"))
        if message.get("role") == "user":
            running_question_count +=1
            start_counting=True
        if start_counting and (question_count- running_question_count>= MAX_HIST):
            removal_indices.append(idx-1)
        elif question_count- running_question_count< MAX_HIST:
            break
            
    # remove items with indices in removal_indices
    # print("removal_indices", removal_indices)
    for index in removal_indices:
        del history[index]
    question_count=0
    # print("done purging history, len history now", len(history ))
    for message in history:
        message = dict(message)

        if message.get("role") == "user":
            question_count +=1
            # print("question_count added, it becomes: ", question_count)   
        if message.get("role") != "system" and message.get("role") != "tool" and message.get("name") is None and len(message.get("content")) > 0:
            with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        elif message.get("role") == "tool":
            data_item = display_data.get(message.get("tool_call_id"), None)

if user_input:
    st.session_state['solution_provided'] = False
    st.session_state['feedback'] = False
    with st.chat_message("user"):
        st.markdown(user_input)
        try:
            # stream_out= False
            
            stream_out, code, history, agent_response,data = agent.run(user_input=user_input,conversation=history)
            history.append({"role": "assistant", "content": agent_response})
        except Exception as e:
            agent_response= None
            print("error in running agent, error is ", e)
            if 'history' in st.session_state:
                st.session_state['history'] = []
            if 'display_data' in st.session_state:
                st.session_state['display_data'] = {}

    with st.chat_message("assistant"):
        if agent_response:
            st.markdown(agent_response)
            st.session_state['solution_provided']= True
            st.session_state['code'] = code
            st.session_state['answer'] = agent_response
            st.session_state['question'] = user_input

            feedback = st.checkbox("That was a good answer", key="feedback")



    # if data is not None:
    #     # print("adding data to session state, data is ", data)
    st.session_state['display_data'] = data

st.session_state['history'] = history
st.session_state['question_count'] = question_count