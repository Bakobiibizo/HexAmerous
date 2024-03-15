from pydantic import BaseModel
from typing import List, Dict, Iterator
from src.templates.interface import BaseTemplate
from abc import ABC, abstractmethod


class Generator(BaseModel, ABC):
    template: BaseTemplate
    url: str
    api_key: str
    context: List
    context_window: int

    def set_apikey(self, apikey) -> bool:
        self.api_key = apikey
        return True

    def set_url(self, url) -> bool:
        self.url = url
        return True
    
    def set_context_window(self) -> bool:
        self.context_window = 16000
        return True
        
    def set_context(self, context) -> List[Dict[str, str]]:
        if not self.context:
            self.context = []
        self.context.append(context)
        return self.context
    
    def set_template(self, template: BaseTemplate) -> List[Dict[str, str]]:
        self.template = template
        if self.context[0]["role"] == "system":
            self.context.pop(0)
        self.context.insert(0, self.template.create_system_prompt())
        return self.context        
        
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, str]:
        pass
    
    @abstractmethod
    async def async_generate(
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