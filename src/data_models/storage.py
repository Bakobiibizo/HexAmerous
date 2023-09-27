import pathlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel, validator
from src.data_models.agents import Agent, AgentAction, agent_sql_table, agent_action_sql_table
from src.data_models.messages import Message, SystemMessage, message_sql_table, system_message_sql_table
from src.data_models.context import Context, context_sql_table
from src.data_models.tools import Tool, Tools, tool_sql_table, tools_sql_table

pathlib_path = pathlib.Path

queries = {
    "AGENT": agent_sql_table,
    "AGENT_ACTION": agent_action_sql_table,
    "MESSAGE": message_sql_table,
    "SYSTEM_MESSAGE": system_message_sql_table,
    "CONTEXT": context_sql_table,
    "TOOL": tool_sql_table,
    "TOOLS": tools_sql_table
}


class StorageEnum(Enum):
    AGENT = Agent
    AGENT_ACTION = AgentAction
    MESSAGE = Message
    SYSTEM_MESSAGE = SystemMessage
    CONTEXT = Context
    TOOL = Tool
    TOOLS = Tools


def get_queries(model: StorageEnum) -> str:
    return queries[model.name]


class StorageModel(BaseModel):
    name: StorageEnum
    model: Any

    @validator('model', pre=True, always=True)
    def validate_model(cls, value: Any, values: Dict[str, Any]) -> Any:
        """
        Validation of the model ensuring its of the StorageEnum type
        """
        if name := values.get('name'):
            expected_type = name.value
            if not isinstance(value, expected_type):
                raise ValueError(f"Model must be an instance of {expected_type}")
        return value


class StorageABC(ABC):
    """
    Database manager for sql style data base.
    """

    def __init__(self, db_connection: Any) -> None:
        """
        Initialize the class
        """
        self.db_connection = db_connection

    @abstractmethod
    def create_table(self) -> None:
        """
        Create a table in the database
        """

    @abstractmethod
    def insert_model(self, name: str, storage_model: StorageModel) -> None:
        """
        Insert a new model
        """

    @abstractmethod
    def get_all_models(self) -> List[Dict[str, str]]:
        """
        Fetch all models
        """

    @abstractmethod
    def update_model(self, name: str, storage_model: StorageModel) -> None:
        """
        Update the database entry for a model
        """

    @abstractmethod
    def delete_model(self, name: str) -> None:
        """
        Delete a model from the database
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection
        """
