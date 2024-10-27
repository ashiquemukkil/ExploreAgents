import io
import logging
import os
import sys
import time
from datetime import datetime
import autogen
import uuid
import warnings

from connectors import CosmosDBClient

from .agent_creation_strategy_factory import AgentCreationStrategyFactory

class Orchestrator:

    def __init__(self, conversation_id: str, client_principal: dict):
        self._setup_logging()

        # Get input parameters
        self.client_principal = client_principal
        self.conversation_id = self._use_or_create_conversation_id(conversation_id)
        self.short_id = self.conversation_id[:8]

        # Initialize connectors
        self.cosmosdb = CosmosDBClient()

        # Get environment variables
        self.conversations_container = os.environ.get('CONVERSATION_CONTAINER', 'conversations')
        self.aoai_resource = os.environ.get('AZURE_OPENAI_RESOURCE', 'openai')
        self.model = os.environ.get('AZURE_OPENAI_CHATGPT_DEPLOYMENT', 'openai-chatgpt')
        self.api_version = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-01')
        self.max_tokens = int(os.environ.get('AZURE_OPENAI_MAX_TOKENS', 1000))
        self.orchestration_strategy = os.getenv('AUTOGEN_ORCHESTRATION_STRATEGY', 'classic-rag')
        self.max_rounds = int(os.environ.get('AUTOGEN_MAX_ROUNDS', 20))
        self.api_key = os.environ.get('AZURE_OPENAI_KEY','')

        # Agent creation strategy        
        self._setup_llm_config()
        self.agent_creation_strategy = AgentCreationStrategyFactory.get_creation_strategy(self.orchestration_strategy)

    ### Main functions

    async def answer(self, ask: str) -> dict:
        """Process user query and generate a response from agents."""
        start_time = time.time()
        conversation, history = await self._get_or_create_conversation()
        agents = self._create_agents_with_strategy(history)
        answer_dict = await self._initiate_group_chat(agents, ask)
        await self._update_conversation(conversation, ask, answer_dict, time.time() - start_time)
        return answer_dict
    
    async def _get_or_create_conversation(self) -> tuple:
        """Retrieve or create a conversation from CosmosDB."""
        conversation = await self.cosmosdb.get_document(self.conversations_container, self.conversation_id)
        if not conversation:
            conversation = await self.cosmosdb.create_document(self.conversations_container, self.conversation_id)
            logging.info(f"[orchestrator] {self.short_id} Created new conversation.")
        else:
            logging.info(f"[orchestrator] {self.short_id} Retrieved existing conversation.")
        return conversation, conversation.get('history', [])
    
    def _create_agents_with_strategy(self, history: str) -> list:
        """Create agents based on the selected strategy."""
        logging.info(f"[orchestrator] {self.short_id} Creating agents using {self.agent_creation_strategy} strategy.")
        return self.agent_creation_strategy.create_agents(self.llm_config, history)

    async def _initiate_group_chat(self, agents: list, ask: str) -> dict:
        """Start the group chat and generate a response."""
        logging.info(f"[orchestrator] {self.short_id} Creating group chat.")
        groupchat = autogen.GroupChat(
            agents=agents, 
            messages=[],
            allow_repeat_speaker=False,
            max_round=self.max_rounds
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

    async def _update_conversation(self, conversation: dict, ask: str, answer_dict: dict, response_time: float):
        """Update conversation in the CosmosDB with the new interaction."""
        logging.info(f"[orchestrator] {self.short_id} Updating conversation.")
        history = conversation.get('history', [])
        history.append({"role": "user", "content": ask})
        history.append({"role": "assistant", "content": answer_dict['answer']})

        interaction = {
            'user_id': self.client_principal['id'],
            'user_name': self.client_principal['name'],
            'response_time': round(response_time, 2)
        }
        interaction.update(answer_dict)

        conversation_data = conversation.get('conversation_data', {'start_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'interactions': []})
        conversation_data['interactions'].append(interaction)

        conversation['conversation_data'] = conversation_data
        conversation['history'] = history
        await self.cosmosdb.update_document(self.conversations_container, conversation)
        logging.info(f"[orchestrator] {self.short_id} Finished updating conversation.")

    ### Utility functions

    def _setup_logging(self):
        """Configure logging for the orchestrator and Azure libraries."""
        logging.getLogger('azure').setLevel(logging.WARNING)
        logging.basicConfig(level=os.environ.get('LOGLEVEL', 'DEBUG').upper())

    def _use_or_create_conversation_id(self, conversation_id: str) -> str:
        """Create a new conversation ID if none is provided."""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            logging.info(f"[orchestrator] Creating new conversation_id. {conversation_id}")
            return conversation_id
        return conversation_id

    def _setup_llm_config(self):
        """Set up the configuration for Azure OpenAI language model."""
        self.llm_config = {
            "config_list": [
                {
                    "model": "chat",
                    "api_key": "",
                    "base_url": "https://oai0-yohpwy4qqbu36.openai.azure.com",
                    "api_type": "azure",
                    "api_version": "2024-02-01"
                    # "azure_ad_token_provider": "DEFAULT"
                }
            ],
            "cache_seed": None  # Workaround for running in Azure Functions (read-only filesystem)
        }
