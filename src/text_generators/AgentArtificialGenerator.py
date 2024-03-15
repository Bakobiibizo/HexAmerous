import json
import os
from src.text_generators.interface import Generator, GeneratorConfig
from src.templates.CodingTemplate import CodingTemplate

config = GeneratorConfig(
    template=CodingTemplate,
    url=os.getenviron.get("AGENT_ARTIFICIAL_URL"),
    apikey=os.getenviron.get("AGENT_ARTIFICIAL_API_KEY"),
    context_window=16000
)

class AgentArtificialGenerator(Generator):
    def __init__(self, input_config: GeneratorConfig) -> None:
        super().__init__()
        self.set_apikey()
        self.set_url()
        self.set_context()
        self.set_context_window()

    def set_template(self) -> bool:
        self.template

      

    def generate_text(self, messages: List[Dict[str, str]]) -> str:     


    def prepare_messages(self, queries: Optional[List[str]]=None, template: Optional[List[Dict[str,str]]]=None, context: Optional[Dict[str, str]]=None) -> List[Dict[str,str]]:
        if not self.context:
            self.context = []
        if template:
            for message in template:
                self.context.append(message)
        if context:
            self.context.append({"role": "system", "content": context})
        if queries:
            for query in queries:
                self.context.append({"role": "user", "content": query})
        return self.context

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