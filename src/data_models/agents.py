"""
Models and abstract base classes for managing agents. Agents should be able to access the context window, tools, and generate messages. They will need corresponding api endpoints for accessing different services and models. Though that is probably a seperate concern that will get its own module.

The final design is to have a meta agent that can construct sub agents that are specialized to a particular task and have them go and complete projects in groups. 
"""
from typing import List, Any, Tuple
from abc import ABC, abstractmethod
from pydantic import BaseModel

from managers.storage_manager import StoragePathDBManager
from models.tools import Tool
from models.messages import Message
from models.context import Context

class AgentAction(BaseModel):
    """
    Model for handling agent actions
    """
    tool: str
    message: str
    expected_result: str
    actual_result: str

class Agent(BaseModel):
    """
    Model for managing agents
    """
    name: str
    path: StoragePathDBManager
    tools: List[Tool]
    context: Context
    message: Message
    actions: List[Tuple[AgentAction, str]]

class AgentABC(ABC):
    """
    Abstract base class for managing agents
    """
    @abstractmethod
    def add_message(self)-> List[Message]:
        """
        add a dict to the message history
        """

    @abstractmethod
    def call_api(self) -> Any:
        """
        Send messages to api end points in the standard llm format.
        """

    @abstractmethod
    def llm_chain(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs)-> List[str]:
        """
        Using prompt templates the model should make a plan of action. The plan should be a list of actions
        """

    @abstractmethod
    def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs)-> List[str]:
        """
        Main planning loop for agent archetecture.
        """
