import io
import logging
import os
import sys
import time
import autogen
import warnings

from .nl2sql_dual_agent_creation_strategy import NL2SQLAgentCreationStrategy
from configs import (
    MAX_ROUNDS,
    OPENAI_KEY,
    OPENAI_CHATGPT_DEPLOYMENT
)

class Orchestrator:

    def __init__(self,conversation_id):
        # Agent creation strategy        
        self._setup_llm_config()
        self.short_id = conversation_id
        self.agent_creation_strategy = NL2SQLAgentCreationStrategy()
        self.max_rounds = MAX_ROUNDS
        self.conversation_id = conversation_id


    def answer(self,history, ask: str) -> dict:
        """Process user query and generate a response from agents."""
        start_time = time.time()
        agents_config = self._create_agents_with_strategy(history)
        answer_dict = self._initiate_group_chat(agents_config, ask)
        return answer_dict
    
    def _create_agents_with_strategy(self, history: str) -> list:
        """Create agents based on the selected strategy."""
        logging.info(f"[orchestrator] {self.short_id} Creating agents using {self.agent_creation_strategy} strategy.")
        return self.agent_creation_strategy.create_agents(self.llm_config, history)

    def _initiate_group_chat(self, agent_config: dict, ask: str) -> dict:
        """Start the group chat and generate a response."""
        logging.info(f"[orchestrator] {self.short_id} Creating group chat.")
        agents =  agent_config["agents"]
        groupchat = autogen.GroupChat(
            agents=agents,
            allowed_or_disallowed_speaker_transitions=agent_config["transitions"],
            speaker_transitions_type='allowed',
            messages=[],
            max_round=self.max_rounds,
        )
        logging.info(f"[orchestrator] {self.short_id} Creating group chat manager.")
        manager = autogen.GroupChatManager(
            groupchat=groupchat, 
            llm_config=self.llm_config
        )
        # Redirect stdout to capture chat execution output 
        captured_output = io.StringIO()
        sys.stdout = captured_output
        # Use warnings library to catch autogen UserWarning
        with warnings.catch_warnings(record=True) as w:
            sys.stdout = sys.__stdout__
            logging.info(f"[orchestrator] {self.short_id} Initiating chat.")
            chat_result = agents[0].initiate_chat(manager, message=ask, summary_method="last_msg")

          
            # print and reset stdout to its default value
            logging.info(f"[orchestrator] {self.short_id} Group chat thought process: \n{captured_output.getvalue()}.")
            sys.stdout = sys.__stdout__

            logging.info(f"[orchestrator] {self.short_id} Generating answer dictionary.")
            answer_dict = {
                "conversation_id": self.conversation_id,
                "answer": "",
                "data_points": "",
                "thoughts": captured_output.getvalue()  # Optional: Capture thought process
            }
            if chat_result and chat_result.summary:
                answer_dict['answer'] = chat_result.summary
                if len(chat_result.chat_history) >= 2 and chat_result.chat_history[-2]['role'] == 'tool':
                    answer_dict['data_points'] = chat_result.chat_history[-2]['content']
            else:
                logging.info(f"[orchestrator] {self.short_id} No valid response generated.")
                # Check if there's a warning with content filtering block
                if len(w) > 0 and 'finish_reason=\'content_filter\'' in str(w[-1].message):
                    answer_dict['answer'] = "The content was blocked due to content filtering."

            return answer_dict

    ### Utility functions

    def _setup_logging(self):
        """Configure logging for the orchestrator and Azure libraries."""
        logging.getLogger('azure').setLevel(logging.WARNING)
        logging.basicConfig(level=os.environ.get('LOGLEVEL', 'DEBUG').upper())

    def _setup_llm_config(self):
        """Set up the configuration for Azure OpenAI language model."""
        self.llm_config = {
            "config_list": [
                {
                    "model": OPENAI_CHATGPT_DEPLOYMENT,
                    "api_key": OPENAI_KEY
                }
            ],
            "cache_seed": None
        }
