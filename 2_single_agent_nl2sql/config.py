import os
from openai import AzureOpenAI
from sqlalchemy import create_engine  

MAX_RUN_PER_QUESTION = 8
MAX_ERROR_RUN = 3
OPENAI_GPT4_DEPLOYMENT = "chat"

AZURE_OPENAI_ENDPOINT = "https://oai0-yohpwy4qqbu36.openai.azure.com"
AZURE_OPENAI_KEY = "0d9e4cd9cda546a498eae2dfa811f281"
client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT, 
    api_key=AZURE_OPENAI_KEY,  
    api_version="2024-02-15-preview"
)

SQLITE_DB_PATH= os.environ.get("SQLITE_DB_PATH","data/northwind.db")
engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}') 


