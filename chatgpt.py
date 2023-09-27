import os
import openai
import loguru
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Optional
from dotenv import load_dotenv
from models import (
    Agent,
    AgentABC,
    Message, 
    MessageABC,
    SystemMessage,
    SystemMessageABC,
    Context, 
    ContextABC, 
    StoragePaths
)

load_dotenv()

logger = loguru.logger

logger.info("Welcome to HexAmerous, your coding assistant!")

path = Path()

system_file_path = path.resolve(StoragePaths.SYSTEM_MESSAGES_PATH)

with system_file_path.open.read("r", encoder="utf-8") as file:
    system_message_dict = json.loads(file.read())


class Chat_Message(Message, MessageABC):
    def __init__(self, role, content):
        super().__init__()
        self.hisotry_path = system_file_path
        self.role = role
        self.content = content
        
    def create_message(self, role=Optional[str], content=Optional[str]):
        if not role:
            role == self.role
        if not content:
            content = self.content
        self.role = role
        self.content = content
        return {role: self.role, self.content: content}
    

class SystemMessageHandler(SystemMessage, SystemMessageABC):
    def __init__(self, messages):
        super().__init__(messages)
        self.name = name
        self.messages: List[Message]= []
        self.name_map: Dict[str, str]= {}
        self.path = StoragePaths.HISTORY_MESSAGES_PATH
        
    def create_message(self, role=Optional[str], content=Optional[str]):
        if not role:
            role == self.role
        if not content:
            content = self.content
        self.role = role
        self.content = content
        return {role: self.role, self.content: content}
    
    def create_system_message(
        self, 
        path: Optional[str], 
        messaage: Optional[str], 
        role: Optional[str]="sytem", 
        content: Optional[str]=None
        ):
        if not path:
            path = self.path
        if not messaage:
            message = Chat_Message(role=role, content=content)
        if not content or role:
            message = Chat_Message(**message)
            
        
system_file_path = path.resolve(StoragePaths.SYSTEM_MESSAGES_PATH)

system_message_dict_item

system_message = SystemMessage(**system_dict_item)


class GPTChatbot():
    def __init__(self, model="gpt-4", log_count=0):
        logger.info("Init gpt_chatbot")
        super().__init__()
        self.model = model
        system_role = "system"
        self.system_message = SystemMessage(**data)
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
