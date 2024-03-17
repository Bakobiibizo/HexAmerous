from pydantic import BaseModel
from typing import List, Dict, Optional
from src.text_generators.interface import (
    Context, 
    OAIMessage
)




class ContextManager(Context):
    def __init__(self, input_config: Optional[Context]):
        super().__init__(input_config or self.config)

    def add_context(self, message: OAIMessage) -> List[OAIMessage]:
        self.context.append(message)
        return self.context

    def remove_context(self, message: OAIMessage) -> List[OAIMessage]:
        self.context.remove(message)
        return self.context

    def clear_context(self) -> List[OAIMessage]:
        self.context = []
        return self.context

    def update_context(self, new_context: List[OAIMessage]) -> List[OAIMessage]:
        self.context = new_context
        return self.context

    def get_context(self) -> List[OAIMessage]:
        return self.context

    def get_context_content(self) -> bool:
        return "".join(message.content for message in self.context)
        