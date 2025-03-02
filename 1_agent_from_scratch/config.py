from openai import OpenAI

OPENAI_KEY = ""
CHAT_MODEL_NAME = "gpt-4o-mini"


client = OpenAI(
    api_key=OPENAI_KEY
)