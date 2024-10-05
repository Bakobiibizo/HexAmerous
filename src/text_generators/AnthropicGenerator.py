import os
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from src.text_generators.interface import Generator, available_generators
from src.templates.handler import 


TEMPLATES = get_template_manager()


class AnthropicGenerator(Generator):
    def __init__(self):
        super().__init__(
            templates=
            url=os.getenv("ANTHROPIC_URL", "https://api.anthropic.com/v1/messages"),
            api=os.getenv("ANTHROPIC_API_KEY"),
            context_window=100000,
            context=[],
        )
        self.client = AsyncAnthropic(api_key=self.api)
        self.model = "claude-3-opus-20240229"
        self.max_tokens = 1024

    async def generate(self, queries: List[str], context: List[str]) -> str:
        messages = self.prepare_messages(queries, context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error in AnthropicGenerator.generate: {e}")

    async def generate_stream(self, queries: List[str], context: List[str]) -> AsyncGenerator[Dict[str, Optional[str]], None]:
        messages = self.prepare_messages(queries, context)
        
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages
            ) as stream:
                async for response in stream:
                    if response.type == "content_block_delta":
                        yield {
                            "message": response.delta.text,
                            "finish_reason": None,
                        }
                yield {
                    "message": "",
                    "finish_reason": "stop",
                }
        except Exception as e:
            raise Exception(f"Error in AnthropicGenerator.generate_stream: {e}")

    def prepare_messages(self, queries: List[str], context: List[str]) -> List[Dict[str, str]]:
        messages = []
        
        if self.template:
            messages.append({"role": "system", "content": self.template.create_system_prompt()})
        
        for ctx in context:
            messages.append({"role": "user", "content": ctx})
            messages.append({"role": "assistant", "content": "Understood."})
        
        query = " ".join(queries)
        messages.append({"role": "user", "content": query})
        
        return messages

    def set_model(self, model: str) -> None:
        self.model = model

    def set_max_tokens(self, max_tokens: int) -> None:
        self.max_tokens = max_tokens

    # Implementing abstract methods
    def set_apikey(self) -> bool:
        if self.api:
            self.client = AsyncAnthropic(api_key=self.api)
            return True
        return False

    def set_url(self) -> bool:
        # Anthropic API URL is set by default in the AsyncAnthropic client
        return True

    def set_context(self) -> bool:
        # Context is managed in the prepare_messages method
        return True

    def set_context_window(self) -> bool:
        # Context window is not directly used in the Anthropic API
        return True

    def set_template(self) -> bool:
        if self.template:
            return True
        return False

def get_anthropic_generator():
    return AnthropicGenerator()

available_generators.add_generator("anthropic", get_anthropic_generator)