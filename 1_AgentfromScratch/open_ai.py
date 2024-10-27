from config import AZURE_OPENAI_ENDPOINT,AZURE_OPENAI_KEY,AZURE_CHAT_DEPLOYMENT_NAME
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT, 
    api_key=AZURE_OPENAI_KEY,  
    api_version="2024-02-15-preview"
)