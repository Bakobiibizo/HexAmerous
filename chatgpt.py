import os
import openai

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
print("- Welcome to HexAmerous, your coding assistant!")

class GPTChatbot:
    def __init__(self, model="gpt-4", log_count=0):
        print("-- init gpt_chatbot")
        super().__init__()

        self.model = model
        self.role = "role"
        self.content = "content"
        system_role = "system"
        system_content = "You are an expert developer with indepth knowledge of Python and Typescript, along with supporting frameworks. You have indepth knowledge of pytorch and jax for machine learning. You are careful to reference your answers and you work step by step through the questions to provide accurate answers. You provide verbose, detailed, and comprehensive answers to questions. You make sure to go through your answers carefully step by step to ensure the information is correct. In addition, you are an expert dev ops specialist and know how to deploy, train, and create machine learning models on TPUs with Google Cloud's machinery."
        print("-- set log count")
        self.log_count = log_count
        print("-- set messages")
        self.system_message = {self.role: system_role, self.content: system_content}
        self.messages = [self.system_message]

    def change_selected_model(self, model="gpt-4"):
        print("- change_selected_model gpt_chatbot")
        self.model = model
        print(f"-- Selected model changed to {model}.")
        return self.model

    def set_messages(self):
        print("- set_messages gpt_chatbot")
        human_content = self.user_message
        human_role = "user"
        self.human_message = {self.role: human_role, self.content: human_content}
        self.messages.append(self.human_message)
        print(f"-- messages set to {self.messages}")
        return self.messages

    def get_response(self, user_message):
        print("- get_response gpt_chatbot")
        self.user_message = user_message
        self.set_messages()
        response = openai.ChatCompletion.create(messages=self.messages, model=self.model)
        print(f"-- completion: {response}")
        self.response = response.choices[0].message.content
        print(f"-- response: {self.response}")
        ai_role = "assistant"
        ai_content = self.response
        self.ai_message = {self.role: ai_role, self.content: ai_content}
        self.messages.append(self.ai_message)
        print(f"-- appened response to messages: {self.ai_message}")
        self.append_interaction_to_chat_log()
        return self.response

    def append_interaction_to_chat_log(self):
        print(
            f"- append interaction to chat log {self.human_message} \n {self.ai_message}"
        )
        self.log_count = self.log_count + 1
        chat_log_entry1 = f"{self.human_message.values} + \n\n"
        chat_log_entry = f"{self.ai_message.values}+ \n\n"
        with open("./log/log_count.txt", "r", encoding="utf-8") as f:
            log_count = str(f.read().strip())
        with open(f"./log/{log_count}.txt", "a", encoding="utf-8") as f:
            f.write(f"{chat_log_entry1}, {chat_log_entry}")
