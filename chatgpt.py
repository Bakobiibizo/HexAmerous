# -*- coding: utf-8 -*-
import os
import requests
from pydantic import BaseModel
from typing_extensions import List, Dict, Union
from datetime import datetime
from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv

from enum import Enum
from src.text_generators.JippityGenerator import get_jippity_generator


load_dotenv()

manager = get_jippity_generator()

client = manager.get_generators()


# Load environment variables
load_dotenv()

openai = OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = os.getenv("OPENAI_BASE_URL")

logger.info("loading HexAmerous")



# Initialize OpenAI

# Initialize variables


logger.info("Welcome to HexAmerous your coding assistant")

selected_model = "Llama3-8b"


class MODEL_LIST(Enum):
    mixtral="mixtral"
    mistral="mistral"
    llava="llava"
    bakllava="bakllava"
    codellama="codellama"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

selected_model = MODEL_LIST.mixtral

def change_selected_model(model: Union[MODEL_LIST, str]):
    selected_model = MODEL_LIST.MIXTRAL_7B
    logger.info(f"Selected model changed to {selected_model}")
    return selected_model


# call openai chat api
logger.info('loading chat_gpt')
context = []


def chat_gpt(user_message):
    context_manager.add_context({
        "role": "user",
        "content": f"{datetime.now()}: {user_message}"
    })
    
    print(context_manager.context)
    body = {
        "model": f"{selected_model}",
        "messages": context_manager.context
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"x-api-key {os.getenv('AGENTARTIFICIAL_API_KEY')}"
    }
    url = os.getenv("AGENTARTIFICIAL_URL")
    logger.info(prompt)

        # Create prompt


    # Call OpenAI's Chat API
    result = openai.chat.completions.create(model=selected_model.value,
    messages=prompt)
    logger.info(result)
    # Read the current value of the counter from a file
    with open("./log/log_count.txt", "r", encoding="utf-8") as f:
        log_count = str(f.read().strip())
    # get response from OpenAI
    if result.status_code == 200:   
        message = result.json()["choices"][0]["message"]
    
    # append log
    with open(f"./log/{log_count}.txt", "a", encoding='utf-8') as f:
        f.write(f"User: {prompt}\nAssistant: {response}\n\n")

            # add context
            context_manager.add_context(message)
            # Return the AI's response
            print(message["content"])
            return message["content"]
