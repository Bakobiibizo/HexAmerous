import json
import os
from typing import List, Dict, Optional
from src.text_generators.interface import Generator, GeneratorConfig
from src.templates.CodingTemplate import CodingTemplate


class AgentArtificialGenerator(Generator):
    config = GeneratorConfig(
       template=CodingTemplate,
       url=os.environ.get("AGENT_ARTIFICIAL_URL"),
       api_key=os.environ.get("AGENT_ARTIFICIAL_API"),
       context=[],
       context_window=16000
    )
    
    def __init__(self, input_config: GeneratorConfig) -> None:
        super().__init__(input_config or self.config)
        self.queries = []
        self.messages = []
        self.prompt = []

    

    def prepare_messages(
        self,
        queries: Optional[List[str]],
        messages: Optional[List[Dict[str, str]]],
        current_context: Optional[List[Dict[str, str]]]
        ) -> List[Dict[str, str]]:
        if not self.context:
            self.prompt = []
            self.prompt.append(
                self.set_template(
                    self.templates.selected_template
                    )
                )
        else:
            self.prompt.append(
                {
                    "role": "system", 
                    "content": "this is the context of the conversation you are having with the user.\n\nCONTEXT:\n"
                }
            )
            for message in self.context:
                self.prompt.append(message)
            for message in current_context:
                self.prompt.append(message)
            self.context.append(
                {
                    "role": "system",
                    "content": "\nEND OF CONTEXT\n\n"
                }
            )
        if messages:
            for message in messages:
                self.prompt.append({"role": "user", "content": message})
        if queries:
            for query in queries:
                self.prompt.append({"role": "user", "content": query})
        return self.prompt

    def agentartificial_generator(self, messages, url="the-roost- agentartificial.ngrok.dev", model="codellama"):
        connnection = http.client.HTTPSConnection(url)
        payload = json.dumps({
          "messages": messages,
          "model": model,
          "streaming": True
        })
        headers = {
          "Authorization": f"Bearer {self.apikey}",
          "Content-Type": "application/json"
        }
        conn.request("POST", "/code", payload, headers)
        res = conn.getresponse()
        return res.read()