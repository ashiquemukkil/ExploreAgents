from config import AZURE_OPENAI_ENDPOINT,AZURE_OPENAI_KEY,AZURE_CHAT_DEPLOYMENT_NAME,OPENAI_KEY
from openai import AzureOpenAI,OpenAI

# client = AzureOpenAI(
#     azure_endpoint = AZURE_OPENAI_ENDPOINT, 
#     api_key=AZURE_OPENAI_KEY,  
#     api_version="2024-02-15-preview"
# )
client = OpenAI(
    api_key=OPENAI_KEY
)