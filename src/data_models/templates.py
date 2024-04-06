from pydantic import BaseModel
from typing import List, Dict
from enum import Enum


class BaseTemplate(BaseModel):
    """
    A base template for creating structured templates with persona, task, example, tools, and system prompts.

    Attributes:
        description (str): The description of the template.
        persona (str): The persona associated with the template.
        task (str): The task described in the template.
        example (str): An example related to the task.
        tools (str): Tools used in the task.
        system_prompt (List[Dict[str, str]]): A list of system prompts with role and content.

    Methods:
        get_template() -> str:
            Returns a formatted template string with persona, task, example, and tools.
        
        update_templates(new_template: "BaseTemplate"):
            Updates the template attributes with a new template.
        
        create_system_prompt():
            Creates a system prompt based on the template content.
    """
    description: str
    persona: str
    task: str
    example: str
    tools: str
    system_prompt: List[Dict[str, str]]

    def get_template(self):
        """
        gets a formatted template string with persona, task, example, and tools
        """
        return f"""
Persona: {self.persona}

Task: {self.task}

Example: {self.example}

Tools: {self.tools}
"""

    def update_templates(self, new_template: "BaseTemplate"):
        """
        updates the template attributes with a new template
        """
        self.persona = new_template.persona
        self.task = new_template.task
        self.example = new_template.example
        self.tools = new_template.tools

    def create_system_prompt(self):
        """
        creates a system prompt based on the template content
        """
        if self.system_prompt is None:
            self.system_prompt = []
        self.system_prompt.append(
            {
                "role": "system",
                "content": self.get_template()
            }
        )
        return self.system_prompt


class AvailableTemplates(Enum):
    CODING: str = "coding"


class Templates(BaseModel):
    selected_template: BaseTemplate
    available_templates: AvailableTemplates
    templates: Dict[str, BaseTemplate] 