import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_api_key():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    if api_key and api_secret:
        return api_key, api_secret
    else:
        raise Exception("API key or secret missing in .env file.")
