import os
from openai import OpenAI
from sqlalchemy import create_engine  

MAX_RUN_PER_QUESTION = 8
MAX_ERROR_RUN = 3


OPENAI_GPT4_MODEL = "gpt-4o-mini"
OPENAI_KEY = ""
client = OpenAI(
    api_key=OPENAI_KEY, 
)

SQLITE_DB_PATH= os.environ.get("SQLITE_DB_PATH","data/northwind.db")
engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}') 


