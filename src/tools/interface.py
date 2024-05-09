from typing import List, Callable
from pydantic import BaseModel


class Tool(BaseModel):
    name: str
    function: Callable
    description: str


class Tools(BaseModel):
    def __init__(self, new_tools: List[Tool]):
        super().__init__()
        self.tools = self.set_tools(new_tools)

    def set_tools(self, new_tools: List[Tool]):
        self.tools = new_tools
        return self.tools

    def add(self, tool: Tool):
        self.tools.append(tool)

    def remove(self, tool: Tool):
        self.tools.remove(tool)

    def clear(self):
        self.tools = []

    def update(self, new_tools: List[Tool]):
        self.tools = new_tools

    def get(self, name: str):
        for tool in self.tools:
            if tool.name == name:
                return tool

    def use(self, name: str, query: str):
        for tool in self.tools:
            if tool.name == name:
                return tool.function(query)

    def list(self):
        returnString = ""
        for tool in self.tools:
            returnString += f"{tool.name}\n"
        return returnString

    def describe(self):
        returnString = ""
        for tool in self.tools:
            returnString += f"{tool.name}: {tool.description}\n"
        return returnString

    def __call__(self, query: str):
        for tool in self.tools:
            if tool.name in query:
                return tool.function(query)
