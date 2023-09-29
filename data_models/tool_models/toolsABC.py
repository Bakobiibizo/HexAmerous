"""
This class is for agent tool creation and management. The agent should be able to read a description of the tools and how to execute the commands. 

I still have to do a bit more exploring for the format and best use of tools.
"""

from abc import ABC, abstractmethod
from data_models.tool_models.toolsSQL import Tool




class ToolABC(ABC):
    """
    Abstract base class for tool management
    """
    @abstractmethod
    def new_tool(self, name:str, description:str, command:str, api:str)-> Tool:
        """
        Create a tool
        """

    @abstractmethod
    def register_tool(self)-> None:
        """
        Register a tool with the hub
        """

    @abstractmethod
    def use_tool(self)-> Any:
        """
        Use a tool's command and call its api
        """

    @abstractmethod
    def edit_tool(self)-> None:
        """
        Edit the fields of a tool
        """




    
class ToolsABC(ABC):
    """
    An abstract base class for tool management
    """

    def __init__(self):
        """
        Abstract base class for manaing tools
        """

    def register_tool(self)-> None:
        """
        Register a tool with the hub
        """

    def retrieve_tool(self, name: str)-> Tool:
        """
        Retrieve a tool from the tools
        """

    def edit_tool(self, name: str, value: str)-> None:
        """
        Edit the fields of a tool
        """

    def delete_tool(self, name: str)-> None:
        """
        Delete a tool from the tools
        """
     