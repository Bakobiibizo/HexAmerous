"""
Models and abstract base classes for managing the context window of agents. the current plan is to just keep a list of messages and store then im a data base. I may modify it to a queue system depending on how it responds under load and with multiple agents. 
Also context window size is a consideration for the future.
"""
from typing import List
from abc import ABC, abstractmethod
from pydantic import BaseModel
from src.data_models.messages import Message, SystemMessage

class Context(BaseModel):
    """
    Model for handling context
    """
    context: List[Message]
    system_message: SystemMessage
    
def context_sql_table():
    return """
    CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    context LIST message_id INTEGER NOT NULL,
    FOREIGN KEY (message_id) REFERENCES message (id)
);"""
    

class ContextABC(ABC):
    """
    Abstract base class for context window management
    """
    @abstractmethod
    def set_context(self)->List[Message]:
        """
        Sets a list of dict strings that are the messages sent and recieved by the agent. This is used to store the personal history of the agent
        pass
        """
    
    @abstractmethod
    def add_context(self)->List[Message]:
        """
        add a dict to the message history
        """
    
    @abstractmethod
    def clear_context(self)-> None:
        """
        clear the context
        """
