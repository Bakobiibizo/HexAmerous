from pydantic import BaseModel
from typing import List, Dict, Iterator
from abc import ABC, abstractmethod
from src.templates.interface import BaseTemplate


class Generator(BaseModel, ABC):
    """
    Interface for Generators.

    @ property template: BaseTemplate
    @ property url: str
    @ property api: str
    @ property context: List
    @ property context_window: int

    @ method set_apikey
    @ method set_url
    @ method set_context
    @ method set_context_window
    @ method set_template
    @ method generate
    @ method generate_stream
    @ method prepare_messages
    """
    template: BaseTemplate
    url: str
    api: str
    context: List
    context_window: int

    @abstractmethod
    def set_apikey(self) -> bool:
        pass

    @abstractmethod
    def set_url(self) -> bool:
        pass

    @abstractmethod
    def set_context(self) -> bool:
        pass
    
    @abstractmethod
    def set_context_window(self) -> bool:
        pass

    @abstractmethod
    def set_template(self) -> bool:
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, str]:
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> Iterator[Dict[str, str]]:
        pass

    @abstractmethod
    def prepare_messages(
        self,
        queries: List[str],
        context: List[Dict[str, str]],
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        pass


class GeneratorConfig(BaseModel):
    template: BaseTemplate
    url: str
    api: str
    context: List
    context_window: int