import os
import openai
import loguru
from pydantic import BaseModel
from typing import Dict List
from dotenv import load_dotenv

load_dotenv()

logger = loguru.logger

logger.info("Welcome to HexAmerous, your coding assistant!")

class GPTChatbot:
    def __init__(self, model="gpt-4", log_count=0):
        logger.info("Init gpt_chatbot")
        super().__init__()
        self.model = model
        system_role = "system"
        self.system_message = 
        logger.info("-- set log count")
        self.log_count = log_count
        logger.info("-- set messages")
        self.system_message = {self.role: system_role, self.content: system_content}
        self.messages = [self.system_message]

    def change_selected_model(self, model="gpt-4"):
        logger.info("- change_selected_model gpt_chatbot")
        self.model = model
        logger.info(f"-- Selected model changed to {model}.")
        return self.model

    def set_messages(self):
        logger.info("- set_messages gpt_chatbot")
        human_content = self.user_message
        human_role = "user"
        self.human_message = {self.role: human_role, self.content: human_content}
        self.messages.append(self.human_message)
        logger.info(f"-- messages set to {self.messages}")
        return self.messages

    def get_response(self, user_message):
        logger.info("- get_response gpt_chatbot")
        self.user_message = user_message
        self.set_messages()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(model=self.model, messages=self.messages)
        logger.info(f"-- completion: {response}")
        self.response = response.choices[0].message.content
        logger.info(f"-- response: {self.response}")
        ai_role = "assistant"
        ai_content = self.response
        self.ai_message = {self.role: ai_role, self.content: ai_content}
        self.messages.append(self.ai_message)
        logger.info(f"-- appened response to messages: {self.ai_message}")
        self.append_interaction_to_chat_log()
        return self.response

    def append_interaction_to_chat_log(self):
        logger.info(
            f"- append interaction to chat log {self.human_message} \n {self.ai_message}"
        )
        self.log_count = self.log_count + 1
        chat_log_entry1 = f"{self.human_message.values} + \n\n"
        chat_log_entry = f"{self.ai_message.values}+ \n\n"
        with open("./log/log_count.txt", "r", encoding="utf-8") as f:
            log_count = str(f.read().strip())
        with open(f"./log/{log_count}.txt", "a", encoding="utf-8") as f:
            f.write(f"{chat_log_entry1}, {chat_log_entry}")

if __name__ == "__main__":
    GPTChatbot()
