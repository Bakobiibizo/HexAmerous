from pydantic import BaseModel
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
from pathlib import Path
from enum import Enum

path = Path()

class StoragePaths(Enum):
    SYSTEM_MESSAGES_PATH=path.cwd() / "docs" / "system_message" / ".json"
    AGENTS_PATH=path.cwd() / "docs" / "agents" / ".json"
    TOOLS_PATH=path.cwd() / "docs" / "tools" / ".json"
    HISTORY_MESSAGES_PATH=path.cwd() / "docs" / "history" / ".json"
    

class Message(BaseModel):
    role: str
    content: str

class SystemMessage(BaseModel):
    name: str
    role: str
    content: str
    path: StoragePaths.SYSTEM_MESSAGES_PATH

class Tool(BaseModel):
    name: str
    description: str
    command: str
    path: StoragePaths.TOOLS_PATH
    
class Context(BaseModel):
    context: List[Message]
    system_message: SystemMessage
    path: StoragePaths.HISTORY_MESSAGES_PATH
    

class AgentAction(BaseModel):
    tool: str
    message: str
    expected_result: str
    actual_result: str
    
class Agent(BaseModel):
    name: str
    tools: List[Tool]
    context: Context
    message: Message
    actions: List[Tuple[AgentAction, str]]

class MessageABC(ABC):
    @abstractmethod
    def create_message(self):
        pass

class SystemMessageABC(self):
    @abstractmethod
    def create_system_message(self):
        pass
    @abstractmethod
    def delete_system_message(self):
        pass
    @abstractmethod
    def edit_system_message(self):
        pass

class ToolABC(ABC):
    @abstractmethod
    def create_tool(self):
        pass
    @abstractmethod
    def register_tool(self):
        pass
    @abstractmethod
    def use_tool(self):
        pass
    @abstractmethod
    def edit_tool(self):
        pass
    
class ContextABC(ABC):
    @abstractmethod
    def set_context(self)->List[Dict[str, str]]:
        # this should be a list of dict strings that are the messages sent and recieved by the agent. This is used to store the personal history of the agent
        pass
    
    @abstractmethod
    def add_context(self)->List[Dict[str, str]]:
        # add a dict to the message history
        pass
    
    @abstractmethod
    def clear_context(self):
        # clear the context
        pass

class AgentABC(ABC):
    @abstractmethod
    def add_message(self)-> str:
        # add a dict to the message history
        pass
    
    @abstractmethod
    def call_api(self) -> Dict[str, str]:
        # Send messages to api end points in the standard llm format.
        pass    
    
    @abstractmethod
    def llm_chain(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs)-> List[str]:
        # Using prompt templates the model should make a plan of action. The plan should be a list of actions
        pass
    
    @abstractmethod
    def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs)-> List[str]:
        pass
    