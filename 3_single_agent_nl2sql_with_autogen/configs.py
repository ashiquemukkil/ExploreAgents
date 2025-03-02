import os
MAX_ROUNDS = int(os.environ.get('AUTOGEN_MAX_ROUNDS', 20))

OPENAI_KEY = os.environ.get('OPENAI_KEY','')
OPENAI_CHATGPT_MODEL = os.environ.get('OPENAI_CHATGPT_MODEL', 'gpt-4o')
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
