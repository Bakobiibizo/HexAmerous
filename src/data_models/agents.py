"""
Models and abstract base classes for managing agents. Agents should be able to access the context window, tools, and generate messages. They will need corresponding api endpoints for accessing different services and models. Though that is probably a seperate concern that will get its own module.

The final design is to have a meta agent that can construct sub agents that are specialized to a particular task and have them go and complete projects in groups. 
"""
from pydantic import BaseModel
from typing import List, Any, Tuple, Optional
from abc import ABC, abstractmethod
from src.data_models.tools import Tool
from src.data_models.messages import Message
from src.data_models.context import Context



class AgentAction(BaseModel):
    """
    Model for handling agent actions
    """
    id: int
    agent_action_id: int
    agent_id: int
    tool_id: int
    command: str
    message: str
    expected_result: str
    actual_result: str
    notes: Optional[str]
    
def agent_action_sql_table():
    return """
    CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER,
    agent_id INTEGER,
    command TEXT NOT NULL,
    message TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    actual_result TEXT NOT NULL,
    notes TEXT,  # Optional, can be NULL
    FOREIGN KEY (tool_id) REFERENCES tools (id),
    FOREIGN KEY (agent_id) REFERENCES agents (id)
);"""

class Agent(BaseModel):
    """
    Model for managing agents
    """
    id: int
    name: str
    tools: List[Tool]
    context: Context
    message: Message
    actions: List[Tuple[AgentAction, str]]
    
def agent_sql_table():
    return """
    CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    context LIST message_id INTEGER NOT NULL,
    message message_id INTEGER NOT NULL,
    actions LIST agent_id INTEGER,
    notes TEXT,  # Optional, can be NULL
    FOREIGN KEY (agent_action_id) REFERENCES agents (id)
    FOREIGN KEY (message_id) REFERENCES message (id)
);"""

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


