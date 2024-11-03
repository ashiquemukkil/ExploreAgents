import os
<<<<<<< HEAD
from openai import AzureOpenAI
=======
from openai import AzureOpenAI,OpenAI
>>>>>>> b6480c1 (initial push)
from sqlalchemy import create_engine  

MAX_RUN_PER_QUESTION = 8
MAX_ERROR_RUN = 3

# OPENAI_GPT4_DEPLOYMENT = "chat"
AZURE_OPENAI_ENDPOINT = "https://oai0-yohpwy4qqbu36.openai.azure.com"
# AZURE_OPENAI_KEY = ""
# client = AzureOpenAI(
#     azure_endpoint = AZURE_OPENAI_ENDPOINT, 
#     api_key=AZURE_OPENAI_KEY,  
#     api_version="2024-02-15-preview"
# )

OPENAI_GPT4_DEPLOYMENT = "gpt-4o-mini"
AZURE_OPENAI_KEY = ""
client = OpenAI(
    api_key=AZURE_OPENAI_KEY, 
)

SQLITE_DB_PATH= os.environ.get("SQLITE_DB_PATH","data/northwind.db")
engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}') 


