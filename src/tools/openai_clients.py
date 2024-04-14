from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

litellm_client = OpenAI(
    api_key=os.getenv("LITELLM_API_KEY"),
    base_url=os.getenv("LITELLM_API_URL"),
)

assistants_client = OpenAI(
    base_url=os.getenv("ASSISTANTS_API_URL"),
)