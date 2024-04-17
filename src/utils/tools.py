from typing import List
from openai.types.beta import AssistantTool
from openai.types.beta.function_tool import FunctionTool
from openai.types.beta.retrieval_tool import RetrievalTool
from openai.types.beta.code_interpreter_tool import CodeInterpreterTool
from pydantic import BaseModel


class ToolItem(BaseModel):
    type: str
    description: str


def tools_to_map(tools: List[AssistantTool]) -> dict[str, ToolItem]:
    """
    Converts a list of AssistantTool objects to a dictionary.
    """
    tools_map = {}
    for tool in tools:
        if isinstance(tool, FunctionTool):
            tools_map[tool.type] = ToolItem(
                type=tool.type,
                description="Generates text based on input data.",
            )
        elif isinstance(tool, RetrievalTool):
            tools_map[tool.type] = ToolItem(
                type=tool.type,
                description="Retrieves information from database containing keys.",
            )
        elif isinstance(tool, CodeInterpreterTool):
            tools_map[tool.type] = ToolItem(
                type=tool.type,
                description="Interprets and executes code.",
            )
    return tools_map

text_generation_tool = ToolItem(
    type="text_generation",
    description="General text response.",
)

completion_tool = ToolItem(
    type="completion",
    description="Completes the task.",
)