import os
import json
import uuid
import pandas as pd
import sys  
import inspect
from io import StringIO  
import contextlib 

from config import client,OPENAI_GPT4_DEPLOYMENT,engine
from prompt import get_system_prompt


def check_args(function, args):
    sig = inspect.signature(function)
    params = sig.parameters

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided 
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False
        
def retrieve_context(business_concepts):
    if business_concepts:
        business_concepts = ' '.join(business_concepts)
    # Load the metadata file
    with open(os.getenv("META_DATA_FILE","data/metadata.json"), "r") as file:
        data = json.load(file)

    # Extract values from the loaded data
    analytic_scenarios = data.get("analytic_scenarios", {})
    scenario_list = [(scenario[0], scenario[1]['description']) for scenario in analytic_scenarios.items()]
    # create  scenario_list_md which is the a markdown table with column headers 'Scenario' and 'Description' from scenario_list
    scenario_list_md = ""
    for scenario in scenario_list:
        scenario_list_md += f"| {scenario[0]} | {scenario[1]} |\n"
    #add headers 'Scenario' and 'Description' to scenario_list_md
    scenario_list_md = f"| Scenario | Description |\n| --- | --- |\n{scenario_list_md}"

    sys_msg = get_system_prompt(scenario_list_md)

    response = client.chat.completions.create(
        model=OPENAI_GPT4_DEPLOYMENT, # The deployment name you chose when you deployed the GPT-35-turbo or GPT-4 model.
        messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": business_concepts}],
    response_format={"type": "json_object"}
    
    )
    
    response_message = response.choices[0].message.content.strip()
    # print("response_message: ", response_message)
    scenario_names = json.loads(response_message)["scenarios"]
    scenario_names = [scenario["scenario_name"] for scenario in scenario_names]

    # Extract values from the loaded data
    analytic_scenarios = data.get("analytic_scenarios", {})
    scenario_list = [scenario[0] for scenario in analytic_scenarios.items()]
    if not set(scenario_names).issubset(set(scenario_list)):
        raise Exception("You provided invalid scenario name(s), please check and try again")
    scenario_tables = data.get("scenario_tables", {})
    scenario_context = "Following tables might be relevant to the question: \n"
    all_tables = data.get("tables", {})
    all_relationships = data.get("table_relationships", {})
    all_relationships = {(relationship[0], relationship[1]):relationship[2] for relationship in all_relationships}
    tables = set()
    for scenario_name in scenario_names:
        tables.update(scenario_tables.get(scenario_name, []))
    for table in tables:
        scenario_context += f"- table_name: {table} - description: {all_tables[table]['description']} - columns: {all_tables[table]['columns']}\n"
    table_pairs = [(table1, table2) for table1 in tables for table2 in tables if table1 != table2]
    relationships = set()
    for table_pair in table_pairs:
        relationship = all_relationships.get(table_pair, None)
        if relationship:
            relationships.add((table_pair[0], table_pair[1], relationship)) 
    
    scenario_context += "\n"
    scenario_context += "\nTable relationships: \n"
    for relationship in relationships:
        scenario_context += f"- {relationship[0]}, {relationship[1]}:{relationship[2]}\n"
    

    scenario_context += "\nFollowing rules might be relevant: \n"
    for scenario_name in scenario_names:
        scenario_context += f"- {scenario_name}: {str(analytic_scenarios[scenario_name]['rules'])}\n"
    return scenario_context


def execute_python_code(assumptions, goal,python_code,execution_context):

    def execute_sql_query(sql_query, limit=100):  
        result = pd.read_sql_query(sql_query, engine)
        result = result.infer_objects()
        for col in result.columns:  
            if 'date' in col.lower():  
                result[col] = pd.to_datetime(result[col], errors="ignore")  
        return result

    if 'execute_sql_query' not in execution_context:
        execution_context['execute_sql_query'] = execute_sql_query 

    # Define a context manager to redirect stdout and stderr  
    @contextlib.contextmanager  
    def captured_output():  
        new_out, new_err = StringIO(), StringIO()  
        old_out, old_err = sys.stdout, sys.stderr  
        try:  
            sys.stdout, sys.stderr = new_out, new_err  
            yield sys.stdout, sys.stderr  
        finally:  
            sys.stdout, sys.stderr = old_out, old_err  
  
    # Use the context manager to capture output  
    with captured_output() as (out, err):  
        try:  
            exec(python_code, execution_context)
            
        except Exception as e:  
            if hasattr(e, 'message'):
                print("with message in exception")
                print(f"{type(e)}: {e.message}", file=sys.stderr)  
            else:
                print(f"{type(e)}: {e}", file=sys.stderr)  

    
    # Retrieve the captured output and errors  
    stdout = out.getvalue()  
    stderr = err.getvalue()  

    new_input=""
    if len(stdout)>0:
        new_input +="\n"+ stdout 
        print(new_input)        
        return execution_context, new_input

    if len(stderr)>0:
        new_input +="\n"+stderr
        print(new_input)
        print(python_code)
        return execution_context, new_input
    
    return execution_context, ''
    

CODER_AVAILABLE_FUNCTIONS = {
    "execute_python_code": execute_python_code,
    "retrieve_context": retrieve_context,
} 