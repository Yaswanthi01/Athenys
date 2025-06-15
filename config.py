import os
from dotenv import load_dotenv

load_dotenv() 

# New SDK variable names
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION')
OPENAI_API_TYPE= os.getenv('OPENAI_API_TYPE', 'azure')  # Default to 'azure' if not set


print('ENV VARS LOADED:')
print('AZURE_OPENAI_ENDPOINT:', AZURE_OPENAI_ENDPOINT)
print('OPENAI_API_VERSION:', OPENAI_API_VERSION)
print('AZURE_OPENAI_API_KEY:', 'SET' if AZURE_OPENAI_API_KEY else 'MISSING')
