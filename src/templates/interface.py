from pydantic import BaseModel
from typing import List, Dict
from enum import Enum


class BaseTemplate(BaseModel):
    description: str
    persona: str
    task: str
    example: str
    tools: str
    system_prompt: List[Dict[str, str]]

    def get_template(self):
        return f"""
Persona: {self.persona}

Task: {self.task}

Example: {self.example}

Tools: {self.tools}
"""

    def update_templates(self, new_template: "BaseTemplate"):
        self.persona = new_template.persona
        self.task = new_template.task
        self.example = new_template.example
        self.tools = new_template.tools

    def create_system_prompt(self):
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