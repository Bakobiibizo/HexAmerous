"""
Template Manager
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Union, Generator, Any
from src.templates.template_interface import TemplateManager, BaseTemplate

class Handler(BaseModel):
    templates: TemplateManager = Field(default_factory=TemplateManager)
    selected_template: str = Field(default_factory=str)
    available_templates: Dict[str, BaseTemplate] = Field(default_factory=dict)
    context: List[Dict[str, str]] = Field(default_factory=list)

class TemplateHandler(TemplateManager):
    """
    Initialize the class with a selected template.

    Parameters:
        selected_template (Union[str, AvailableTemplates]): The selected template, which can be a string or an AvailableTemplates enum value.

    Returns:
        None
    """

    def __init__(self, selected_template: str):
        super().__init__()
        self.templates = TemplateManager()
        self.selected_template = self.select_template(selected_template)
        self.available_templates = TemplateManager().get_all_fields()
        self.system_prompt = self.get_system_prompt()

    def get_system_prompt(self) -> Dict[str, str]:
        """
        Get the template and return a system prompt based on the selected template.

        Parameters:
            self: The object instance
        Returns:
            Dict[str, str]: The system prompt based on the selected template
        """
        return self.templates[self.selected_template].create_system_prompt()

    
if __name__ == "__main__":
    print(TemplateHandler().get_all_fields())
