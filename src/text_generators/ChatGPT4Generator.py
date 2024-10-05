import contextlib
import os
from loguru import logger
from openai import OpenAI
from typing import List, Dict, AsyncGenerator
from src.text_generators.interface import Generator, GPT4GeneratorError

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
        self.model = os.getenv("OPENAI_MODEL")
        self.context_window = 10000
        self.context = {}
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")

    async def generate(
        self,
        queries: List[str],
        context: List[str],
    ) -> str:
        self.set_context(context)
        messages = self.prepare_messages(queries, self.context)

        try:
            completion = openai.chat.completions.create(messages, model=self.model_name)
            system_msg = str(completion["choices"][0]["message"]["content"])

        except GPT4GeneratorError as e:
            logger.error(f"Error in GPT4Generator.generate: {e}")
        return system_msg

    async def generate_stream(
        self,
        queries: List[str],
        context: List[str] = None
    ) -> AsyncGenerator[Dict]:
        self.set_context(context)
        messages = self.prepare_messages(queries, self.context)

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
        except GPT4GeneratorError as e:
            logger.error(f"Error in GPT4Generator.generate_stream {e}")

    def prepare_messages(
        self, queries: List[str], context: List[str]
    ) -> Dict[str, str]:
        messages.extend([message for message in self.context])
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
        return bool(self.api_key)

    def set_url(self, url=None) -> bool:
        if url is None:
            url = os.getenv("OPENAI_URL")
        self.base_url = url
        self.set_generator()
        return bool(self.base_url)
        
    def set_generator(self, generator=None):
        if generator is None:
            generator = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        self.generator = generator
        return bool(self.generator)
        
    def set_model(self, model=None):
        if model is None:
            model = os.getenv("OPENAI_MODEL")
        self.model = model
        return bool(self.model)
        
    def set_context(self, context=None) -> bool:
        if context is None:
            context = {}
        self.context = context
        return bool(self.context)

    def set_context_window(self, context_window=None) -> bool:
        if self.context_window is None:
            context_window = 16000
        self.context_window = context_window
        return bool(self.context_window)


def get_GPT4Generator():
    return GPT4Generator
