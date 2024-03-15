import json
import os
from src.text_generators.interface import Generator, GeneratorConfig
from src.templates.CodingTemplate import

config = GeneratorConfig(
    template=CodingTemplate(),
    url=os.getenviron.get("AGENT_ARTIFICIAL_URL"),
    apikey=os.getenviron.get("AGENT_ARTIFICIAL_API_KEY"),
    context_window=16000
)

class AgentArtificialGenerator(Generator):
    def __init__(
        self,
        template=None,
        url="",
        apikey="",
        context=None,
        context_window=16000
    ) -> None:
        super().__init__()
        self.url = url
        self.apikey = apikey
        self.context = context
        self.context_window = context_window
        self.agentartificial_generator = template

    def set_configuration(self, config: GeneratorConfig):
        self.apikey = os.environ.get("AGENT_ARTIFICIAL_API_KEY")
        self.url = os.environ.get("AGENT_ARTIFICIAL_URL")
        self.context_window = 16000
        self.template =

    def install_depenedencies(self):
        import http.client
      

    def generate_text(self, messages, url="the-roost- agentartificial.ngrok.dev", model="codellama"):
        return self.agentartificial_generator(messages, url, model)        


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