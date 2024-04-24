import json
import os
import httpx
from typing import List, Dict, Optional, Callable
from src.text_generators.interface import Generator, GeneratorConfig
from src.templates.interface import AvailableTemplates, templates, base_template
from dotenv import load_dotenv

load_dotenv()




class AgentArtificialGenerator(Generator):
    def __init__(self) -> None:
        config = self.set_configuration(
            template=templates.templates[AvailableTemplates.CODING],
            url=str(os.getenv("AGENTARTIFICIAL_URL")), api=str(os.getenv("AGENTARTIFICIAL_API_KEY")),
            context_window=10000,
            context=[]
        )
        super().__init__(**config)

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
      

    def generate_text(
        self, 
        messages, 
        url="agentartificial.ngrok.dev", 
        model="llama3-7b"):
        messages = self.prepare_messages(queries=messages)
        return self.agentartificial_generator(
            messages=messages, 
            url=url, 
            model=model
            )

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

    def agentartificial_generator(self, messages, url="the-roost- agentartificial.ngrok.dev", model="codellama"):
        client = httpx.Client()
        payload = {
          "messages": messages,
          "model": model,
          "streaming": True
        }
        headers = {
          "Authorization": f"Bearer {self.api}",
          "Content-Type": "application/json"
        }
        res = client.post(url, data=payload, headers=headers)
        return res.read()

