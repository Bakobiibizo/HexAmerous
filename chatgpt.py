# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel
from typing_extensions import List, Dict, Union
from datetime import datetime
from loguru import logger
from enum import Enum

# Load environment variables
load_dotenv()

print("loading HexAmerous")

logger.info("Welcome to HexAmerous your coding assistant")

selected_model = "Llama3-8b"


class MODEL_LIST(Enum):
    LLAMA3_7B = "Llama3-7b"
    LLAMA3_70B = "Llama3-70b"
    MIXTRAL_7B = "Mixtral-7b"
    MIXTRAL_70B = "Mixtral-70b"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


def change_selected_model(model: Union[MODEL_LIST, str]):
    selected_model = MODEL_LIST.MIXTRAL_7B
    logger.info(f"Selected model changed to {selected_model}")
    return selected_model


# call openai chat api


class Manager(BaseModel):
    context: List[Dict[str, str]] = []
    context_counts: List[float] = []
    full_count: Union[int, float] = 0


class ContextManager(Manager):
    def __init__(self, context: Dict[str, str]):
        super().__init__()
        self.context = []
        self.add_context(context)
        self.context_counts = [self.rough_context_counter(context["content"])]
        self.full_count = self.get_count()

    def add_context(self, message: Dict[str, str]):
        self.context.append(message)

    def rough_context_counter(self, context: str):
        text = f"{context}"
        words = text.split(" ")
        rough_count = len(words) * 0.6
        self.context_counts.append(rough_count)
        self.check_context()
        return rough_count

    def get_count(self):
        if not self.context:
            return 0
        if len(self.context_counts) == 1:
            return self.context_counts[0]
        return sum(self.context_counts)

    def check_context(self):
        full_count = self.get_count()
        messages_count = len(self.context_counts)
        while full_count > 8000:
            value = self.context_counts.pop(0)
            full_count -= value
            messages_count -= 1
            self.context.pop(0)
            self.context_counts.pop(0)

            full_count += count
            print(full_count)
            if full_count > 16000:
                remove_count = messages_count - i
                while remove_count > 0:
                    self.context_counts.pop(remove_count - 1)
                    self.context.pop(remove_count - 1)
        print(self.context)
        return self.context


system_prompt = {"role": "system", "content": "You are a helpful assistant."}


def get_context_manager():
    return ContextManager(context=system_prompt)


context_manager = get_context_manager()

print("loading")


context_manager.add_context({"role": "user", "content": "Hi there, how are you today?"})

context_manager.add_context(
    {
        "role": "assistant",
        "content": "I am doing well, thank you for asking. I am learning a lot about the world and I am excited to learn more. What can I help you with today?",
    }
)


def chat_gpt(user_message):
    context_manager.add_context(
        {"role": "user", "content": f"{datetime.now()}: {user_message}"}
    )

    print(context_manager.context)
    body = {"model": f"{selected_model}", "messages": context_manager.context}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"x-api-key {os.getenv('AGENTARTIFICIAL_API_KEY')}",
    }
    url = os.getenv("AGENTARTIFICIAL_URL")
    # Call OpenAI's Chat API
    result = requests.post(url=str(url), json=body, headers=headers)
    print(result)
    # Read the current value of the counter from a file
    with open("./log/log_count.txt", "r", encoding="utf-8") as f:
        log_count = str(f.read().strip())
    # get response from OpenAI
    if result.status_code == 200:
        message = result.json()["choices"][0]["message"]

        # append log
        with open(f"./log/{log_count}.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {user_message}\n\nAssistant: {message['content']}\n\n")

            # add context
            context_manager.add_context(message)
            # Return the AI's response
            print(message["content"])
            return message["content"]
