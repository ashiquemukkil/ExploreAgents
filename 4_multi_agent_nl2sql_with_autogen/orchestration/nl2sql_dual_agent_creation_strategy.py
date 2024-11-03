import logging
import json
import sqlparse
from autogen import UserProxyAgent, AssistantAgent, register_function
from tool.utils import get_time,get_today_date
from orchestration.base_agent_creation_strategy import BaseAgentCreationStrategy
from typing import Optional, List, Dict, Union
from pydantic import BaseModel
import sqlite3



# Define Pydantic models for the return types
class SchemaInfo(BaseModel):
    table_name: Optional[str] = None
    description_long: Optional[str] = None
    description_short: Optional[str] = None
    columns: Optional[Dict[str, str]] = None
    column_name: Optional[str] = None
    column_description: Optional[str] = None
    error: Optional[str] = None

class TablesList(BaseModel):
    tables: List[Dict[str, Union[str, List[str]]]]

class ValidateSQLResult(BaseModel):
    is_valid: bool
    error: Optional[str] = None

class ExecuteSQLResult(BaseModel):
    results: Optional[List[Dict[str, Union[str, int, float, None]]]] = None
    error: Optional[str] = None

class NL2SQLAgentCreationStrategy(BaseAgentCreationStrategy):
    def __init__(self):
        # Load the data dictionary JSON file
        data_dictionary_path = 'config/data_dictionary.json'
        with open(data_dictionary_path, 'r') as f:
            self.data_dictionary = json.load(f)

        self.database = 'data/northwind.db'
        self.connection = self.create_connection()
        self.cursor = self.connection.cursor()
    
    def create_connection(self):

        try:
            connection = sqlite3.connect(self.database)
            return connection
        except Exception as e:
            print("#####")
            logging.err

        
    
    def create_agents(self, llm_config, history):
        """
        Creates agents and registers functions for the NL2SQL dual agent scenario.
        """

        # Create User Proxy Agent
        user_proxy_prompt = self._read_prompt("user_proxy")
        user_proxy = UserProxyAgent(
            name="user",
            system_message=user_proxy_prompt,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
        )

        # Create Assistant Agent
        conversation_summary = self._summarize_conversation(history)
        assistant_prompt = self._read_prompt("nl2sql_assistant", {"conversation_summary": conversation_summary})
        assistant = AssistantAgent(
            name="assistant",
            description="Generates SQL queries, considers advisor recommendations, and executes queries after feedback.",
            system_message=assistant_prompt,
            human_input_mode="NEVER",
            llm_config=llm_config,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
        )

        # Create Advisor Agent
        advisor_prompt = self._read_prompt("advisor")
        advisor = AssistantAgent(
            name="advisor",
            description="Reviews and rewrites SQL queries as needed for optimal execution.",
            system_message=advisor_prompt,
            human_input_mode="NEVER",
            llm_config=llm_config
        )
        
        # def get_schema_info(table_name: Optional[str] = None, column_name: Optional[str] = None) -> SchemaInfo:
        #     return self._get_schema_info(table_name, column_name)

        def get_all_tables_info() -> TablesList:
            """
            Retrieve a list of all tables with their descriptions from the data dictionary.
            """
            tables_info = []
            for table_name, table_info in self.data_dictionary.items():
                tables_info.append({
                    'table_name': table_name,
                    'description_long': table_info.get("description_long")
                })
            return TablesList(tables=tables_info)

        def validate_sql_query(query: str) -> ValidateSQLResult:
            """
            Validate the syntax of an SQL query.
            Returns {'is_valid': True} if valid, or {'is_valid': False, 'error': 'error message'} if invalid.
            """
            try:
                parsed = sqlparse.parse(query)
                if parsed and len(parsed) > 0:
                    # Additional checks can be added here if needed
                    return ValidateSQLResult(is_valid=True)
                else:
                    return ValidateSQLResult(is_valid=False, error="Query could not be parsed.")
            except Exception as e:
                return ValidateSQLResult(is_valid=False, error=str(e))

        def execute_sql_query(query: str) -> ExecuteSQLResult:
            """
            Execute an SQL query and return the results.
            Returns a list of dictionaries, each representing a row.
            """
            try:
                # Limit to SELECT statements only for safety
                if not query.strip().lower().startswith('select'):
                    return ExecuteSQLResult(error="Only SELECT statements are allowed.")

                self.cursor.execute(query)
                columns = [column[0] for column in self.cursor.description]
                rows = self.cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                return ExecuteSQLResult(results=results)
            except Exception as e:
                return ExecuteSQLResult(error=str(e))     

        # Register functions with assistant and user_proxy
        # register_function(
        #     get_schema_info,
        #     caller=assistant,
        #     executor=user_proxy,
        #     name="get_schema_info",
        #     description="Retrieve a list of all table names and their descriptions from the data dictionary."
        # )

        register_function(
            get_all_tables_info,
            caller=assistant,
            executor=user_proxy,
            name="get_all_tables_info",
            description="Retrieve table information from the data dictionary. Provide table_name or column_name to get information about the table or column."
        )

        register_function(
            execute_sql_query,
            caller=assistant,
            executor=user_proxy,
            name="execute_sql_query",
            description="Execute an SQL query and return the results as a list of dictionaries. Each dictionary represents a row."
        )

        register_function(
            validate_sql_query,
            caller=advisor,
            executor=user_proxy,
            name="validate_sql_query",
            description="Validate the syntax of an SQL query. Returns is_valid as True if valid, or is_valid as False with an error message if invalid."
        )

        register_function(
            get_today_date,
            caller=assistant,
            executor=user_proxy,
            name="get_today_date",
            description="Provides today's date in the format YYYY-MM-DD."
        )

        register_function(
            get_time,
            caller=assistant,
            executor=user_proxy,
            name="get_time",
            description="Provides the current time in the format HH:MM."
        )

        # Define allowed transitions between agents
        allowed_transitions = {
            user_proxy: [assistant],
            advisor: [user_proxy, assistant],
            assistant: [advisor, user_proxy],
        }
        
        # Return agent configuration
        agent_configuration = {
            "agents": [user_proxy, assistant, advisor],
            "transitions": allowed_transitions,
            "transitions_type": "allowed"
        }

        return agent_configuration