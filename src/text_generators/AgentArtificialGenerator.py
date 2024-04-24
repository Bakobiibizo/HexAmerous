import os
import json
import httpx
from typing import List, Dict, Optional, Callable, Iterator
from src.text_generators.interface import Generator, GeneratorConfig, available_generators
from src.templates.interface import AvailableTemplates, templates, base_template
from dotenv import load_dotenv

load_dotenv()


class AgentArtificialGenerator(Generator):
    def __init__(
        self,
        template=templates.templates[AvailableTemplates.CODING],
        url=str(os.getenv("AGENTARTIFICIAL_URL")),
        api=str(os.getenv("AGENTARTIFICIAL_API_KEY")),
        context_window=10000,
        context=[],
        model="llama3_8b"
        ):
        super().__init__(
            template=template,
            url=url,
            api=api,
            context_window=context_window,
            context=context      
        )
        self.model = model
        self.client = httpx.Client()
        
    def set_apikey(self) -> bool:
        return bool(self.api)

    def set_url(self) -> bool:
        return bool(self.url)

    def set_context(self) -> bool:
        return bool(self.context)

    def set_context_window(self) -> bool:
        return bool(self.context_window)

    def set_template(self) -> bool:
        return bool(self.template)
    
    def set_configuration(self, template: Callable, url: str, api: str, context_window: int, context: List[Dict[str, str]]):
        return GeneratorConfig(
            template=template(),
            url=url,
            api=api,
            context_window=context_window,
            context=context
        ).model_dump()

    def install_depenedencies(self):
        try:
            import httpx  # type: ignore
            if not httpx:
                raise ImportError
        except ImportError:
            os.system("pip install httpx")

    def prepare_messages(
        self, 
        queries: Optional[List[str]]=None
        ) -> List[Dict[str,str]]:
        
        if not self.context:
            self.context = [self.template.create_system_prompt()]  # type: ignore
        if not queries:
            return self.context
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            self.context.append(base_template.create_message(query))
        if queries:
            for query in queries:
                self.context.append({"role": "user", "content": query})
        return self.context

    def prepare_body(self):
        return {
            "model": self.model,
            "messages": self.context
        }

    def generate(
        self,
        queries,
        url
        ):
        self.prepare_messages(queries=queries)
        body = self.prepare_body()
        response = self.client.post(url, json=json.dumps(body))
        return response.json()
        
    async def generate_stream(self, messages, url="the-roost- agentartificial.ngrok.dev", model="codellama"):
        
        payload = {
          "messages": messages,
          "model": model,
          "streaming": True
        }
        headers = {
          "Authorization": f"Bearer {self.api}",
          "Content-Type": "application/json"
        }
        res = self.client.post(url, data=payload, headers=headers)
        yield res.read()

def get_agentartificial_generator():
    return AgentArtificialGenerator()

available_generators.add_generator("agent_artificial", get_agentartificial_generator)