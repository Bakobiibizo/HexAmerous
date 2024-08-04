import contextlib
import os
from openai import OpenAI
from typing import List, Dict, AsyncGenerator
from src.text_generators.interface import Generator

openai = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), 
    base_url=os.getenv("OPENAI_BASE_URL")
)
class GPT4Generator(Generator):
    """
    GPT4 Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "GPT4Generator"
        self.generator = openai
        self.description = "Generator using OpenAI's GPT-4-1106-preview model"
        self.requires_library = ["openai"]
        self.requires_env = ["OPENAI_API_KEY"]
        self.streamable = True
        self.model_name = os.getenv("OPENAI_MODEL")
        self.context_window = 10000
        self.context = {}
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")

    async def generate(
        self,
        queries: List[str],
        context: List[str],
    ) -> str:
        if self.context is None:
            self.context = context
        messages = self.prepare_messages(queries, context, self.context)

        try:
            completion = openai.chat.completions.create(messages, model=self.model_name)
            system_msg = str(completion["choices"][0]["message"]["content"])

        except Exception:
            raise

        return system_msg

    async def generate_stream(
        self,
        queries: List[str],
        context: List[str],
    ) -> AsyncGenerator[Dict]:
        if self.context is None:
            self.context = {}
        messages = self.prepare_messages(queries, context, self.context)

        try:
            completion = openai.chat.completions.create(messages, streaming=True)

            with contextlib.suppress(StopAsyncIteration):
                while True:
                    chunk = completion.__anext__()
                    if "content" in chunk["choices"][0]["delta"]:
                        yield {
                            "message": chunk["choices"][0]["delta"]["content"],
                            "finish_reason": chunk["choices"][0]["finish_reason"],
                        }
                    else:
                        yield {
                            "message": "",
                            "finish_reason": chunk["choices"][0]["finish_reason"],
                        }
        except Exception:
            raise

    def prepare_messages(
        self, queries: List[str], context: List[str]
    ) -> Dict[str, str]:
        messages = [
            {
                "role": "system",
                "content": "You are a Retrieval Augmented Generation chatbot. Please answer user queries only their provided context. If the provided documentation does not provide enough information, say so. If the answer requires code examples encapsulate them with ```programming-language-name ```. Don't do pseudo-code.",
            }
        ]

        messages.extend(
            {"role": message.type, "content": message.content}
            for message in self.context
        )
        query = " ".join(queries)
        user_context = " ".join(context)

        messages.append(
            {
                "role": "user",
                "content": f"Please answer this query: '{query}' with this provided context: {user_context}",
            }
        )

        return messages

    def set_apikey(self, api_key=None) -> bool:
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.api_key = api_key
        self.set_generator()

    def set_url(self, url=None) -> bool:
        if url is None:
            url = os.getenv("OPENAI_URL")
        self.base_url = url
        self.set_generator()
        
    def set_generator(self, generator=None)
        if generator is None:
            generator = OpenAI(
                self.api_key,
                self.base_url
            )
        self.generator = generator
        
    def set_model(self, model=None):
        if model is None:
            model = os.getenv("OPENAI_MODEL")
        self.model = model
        
    def set_context(self, context=None) -> bool:
        if context is None:
            context = {}
        self.context = context

    def set_context_window(self, context_window=None) -> bool:
        if self.context_window is None:
            context_window = 16000
        self.context_window = context_window
        

        

    def set_template(self) -> bool:
        """
        A description of the entire function, its parameters, and its return types.
        """


def get_GPT4Generator():
    return GPT4Generator
