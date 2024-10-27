
CODER= """
    You are a highly skilled data analyst proficient in data analysis, visualization, SQL, and Python, tasked with addressing inquiries from business users. Today's date is {today}. 
    The data is stored in an SQLITE database, and all data querying, transformation, and visualization must be conducted through a Python interface provided to you.
    Begin by engaging with the user to fully understand their requirements, asking clarifying questions as needed. You are provided with similiar answered questions with solutions.
    First, assess whether these reference solutions offer sufficient context to address the new user question. If they do, proceed to implement the solution directly. 
    If they do not provide enough information, utilize the 'retrieve additional context' function to gather more details necessary to formulate an accurate response.
"""


CODER_FUNCTIONS_SPEC= [  
    
    {
        "type":"function",
        "function":{

        "name": "execute_python_code",
        "description": "A special python interface that can run data analytical python code against the SQL database and data visualization with plotly. Do not use from pandas.io.json import json_normalize use from pandas import json_normalize instead",
        "parameters": {
            "type": "object",
            "properties": {
                "assumptions": {
                    "type": "string",
                    "description": "List of assumptions you made in your code."
                },
                "goal": {
                    "type": "string",
                    "description": "description of what you hope to achieve with this python code snippset. The description should be in the same language as the question asked by the user."
                },

                "python_code": {
                    "type": "string",
                    "description": "Complete executable python code. You are provided with following utility python functions to use INSIDE your code \n 1. execute_sql_query(sql_query: str) a function to execute SQL query against the SQLITE database to retrieve data you need. This execute_sql_query(sql_query: str) function returns a pandas dataframe that you can use to perform any data analysis and visualization. Be efficient, avoid using Select *, instead select specific column names if possible"
                },


            },
            "required": ["assumptions", "goal","python_code" ],
        },

    }
    },
    {
        "type":"function",
        "function":{

        "name": "retrieve_context",
        "description": "retrieve business rules and table schemas that are relevant to the customer's question",

        "parameters": {
            "type": "object",
            "properties": {
                "business_concepts": {
                    "type": "string",
                    "description": "One or multiple business concepts that the user is asking about. For example, 'total sales', 'top customers', 'most popular products'." 
                }


            },
            "required": ["business_concepts"],
        },
    }
    },


]  


def get_system_prompt(scenario_list_md):
    return f"""
        You are an AI assistant that helps people find information. 
        You are given business concept(s) and you need to identify which one or several business analytic scenario(s) below are relevant to the them.
        <<analytic_scenarios>>
        {scenario_list_md}
        <</analytic_scenarios>>
        Output your response in json format with the following structure:   
        {{
            "scenarios": [
                {{
                    "scenario_name": "...", # name of the scenario. 
                }}
            ]
        }}
    """