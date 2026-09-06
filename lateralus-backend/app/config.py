import os

from dotenv import load_dotenv

load_dotenv()

try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
    print("OPENAI_API_KEY found in environment variables.")
except KeyError:
    raise KeyError(
        "OPENAI_API_KEY not found in environment variables. Please set it in your .env file."
    )
