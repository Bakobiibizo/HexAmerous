import pathlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel, validator
from src.data_models.agents import Agent, AgentAction, agent_sql_table, agent_action_sql_table
from src.data_models.messages import Message, SystemMessage, message_sql_table, system_message_sql_table
from src.data_models.context import Context, context_sql_table
from src.data_models.tools import Tool, Tools, tool_sql_table, tools_sql_table

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



