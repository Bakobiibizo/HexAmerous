# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Union, List, Dict
from loguru import logger
from src.generators.manager import GeneratorManager

manager= GeneratorManager()

client = manager.get_generators()

from enum import Enum
# Load environment variables
load_dotenv()

openai = OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = "https://the-roost-agentartificial.ngrok.app"

logger.info("loading HexAmerous")



# Initialize OpenAI

# Initialize variables


logger.info("Welcome to HexAmerous your coding assistant")




logger.info('change_selected_model')


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
    selected_model = MODEL_LIST
    logger.info(f"Selected model changed to {selected_model}")
    return selected_model


# call openai chat api
logger.info('loading chat_gpt')
context = []


def chat_gpt(user_message):
    logger.info(prompt)

        # Create prompt


    # Call OpenAI's Chat API
    result = openai.chat.completions.create(model=selected_model.value,
    messages=prompt)
    logger.info(result)
    # Read the current value of the counter from a file
    with open("./log/log_count.txt", "r", encoding='utf-8') as f:
        log_count = str(f.read().strip())
        # get response from OpenAI
    response = result.choices[0].message.content

    # append log
    with open(f"./log/{log_count}.txt", "a", encoding='utf-8') as f:
        f.write(f"User: {prompt}\nAssistant: {response}\n\n")

    # add context
    context.append(f"User: {prompt}\nAssistant: {response}\n\n")
    # Return the AI's response
    logger.info(response)
    return response
