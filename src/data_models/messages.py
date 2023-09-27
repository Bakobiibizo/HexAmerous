"""
A module for message creation and management. Everyone seem to have adopted the OpenAI messaging format so I decided to follow suit. 
message = [{
    "role": "user/assistant/system",
    "content":"some content"
}]
Everything I will add will be in this format.
"""
from typing import List, Dict, Union
from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel

from managers.storage_manager import StoragePathDBManager

class Message(BaseModel):
    """
    Pydantic model for data sent and recieved by the agent
    """
    role: str
    content: str

class SystemMessage(BaseModel):
    """
    Model for managing system messages
    """
    messages: List[Message]
    name_map: Dict[str, str]
    path: StoragePathDBManager


class MessageABC(ABC):
    """
    Abstract base class for message models
    """
    @abstractmethod
    def create_message(self):
        """
        Convert role and content into message object
        """

class SystemMessageABC(ABC):
    """"
    Abstract base class for System Messages
    """
    @abstractmethod
    def create_system_message(self)->Union[List[Message], Dict[str], Enum]:
        """
        Convert role and content into message object
        """
    @abstractmethod
    def delete_system_message(self)-> None:
        """
        Delete a system message from the system messages
        """
    @abstractmethod
    def edit_system_message(self)-> None:
        """
        Edit a system message in system messages
        """
