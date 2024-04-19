from enum import Enum
from typing import List
from openai.types.beta import AssistantTool
from openai.types.beta.function_tool import FunctionTool
from openai.types.beta.retrieval_tool import RetrievalTool
from openai.types.beta.code_interpreter_tool import CodeInterpreterTool
from pydantic import BaseModel


class Actions(Enum):
    # function, retrieval, code_interpreter, text_generation, completion
    FUNCTION = "function"
    RETRIEVAL = "retrieval"
    CODE_INTERPRETER = "code_interpreter"
    TEXT_GENERATION = "text_generation"
    COMPLETION = "completion"
    FAILURE = "failure"


Actions["FAILURE"]


class ActionItem(BaseModel):
    type: str
    description: str


def actions_to_map(actions: List[str]) -> dict[str, ActionItem]:
    """
    Converts a list of AssistantTool objects to a dictionary.
    """
    actions_map = {}
    for action in actions:
        if action == Actions.TEXT_GENERATION.value:
            actions_map[action] = ActionItem(
                type=Actions.TEXT_GENERATION.value,
                description="Communicate to the user either to summarize or express the next tasks to be executed.",
            )
        elif action == Actions.COMPLETION.value:
            actions_map[action] = ActionItem(
                type=Actions.COMPLETION.value,
                description="Indicate that the current goal is achieved or that this loop should be terminated.",
            )
    return actions_map


def tools_to_map(tools: List[AssistantTool]) -> dict[str, ActionItem]:
    """
    Converts a list of AssistantTool objects to a dictionary.
    """
    tools_map = {}
    for tool in tools:
        if isinstance(tool, FunctionTool):
            tools_map[tool.type] = ActionItem(
                type=tool.type,
                description="Generates text based on input data.",
            )
        elif isinstance(tool, RetrievalTool):
            tools_map[tool.type] = ActionItem(
                type=tool.type,
                description="Retrieves information from database containing keys.",
            )
        elif isinstance(tool, CodeInterpreterTool):
            tools_map[tool.type] = ActionItem(
                type=tool.type,
                description="Interprets and executes code.",
            )
    return tools_map


text_generation_tool = ActionItem(
    type="text_generation",
    description="General text response.",
)

completion_tool = ActionItem(
    type="completion",
    description="Completes the task.",
)
