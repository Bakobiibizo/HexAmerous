from pydantic import BaseModel, Field
from typing import List, Dict
from src.templates.interface import TemplateManager, BaseTemplate


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

    def __init__(self, selected_template: str=None):
        super().__init__()
        self.templates = TemplateManager()
        if not selected_template:
            self.cli_select_template()
        self.selected_template = self.get_template(selected_template)
        self.available_templates = TemplateManager().get_all_fields()
        self.system_prompt = self.get_system_prompt()

    def get_selected_template(self, selected_template: str) -> str:
        self.selected_template = self.templates.get_template(selected_template)
        return self.selected_template
    
    def get_system_prompt(self) -> Dict[str, str]:
        """
        Get the template and return a system prompt based on the selected template.

        Parameters:
            self: The object instance
        Returns:
            Dict[str, str]: The system prompt based on the selected template
        """
        return self.templates.get_template(self.selected_template).create_system_prompt()
    
    def cli_select_template(self):
        print("Available Templates:")
        for template in self.templates.get_all_fields().keys():
            print(template)
        selected_template = input("Enter the name of the template you want to use: ")
        self.selected_template = selected_template


def get_template_manager(selected_template: str):
    return TemplateHandler(selected_template)

if __name__ == "__main__":
    print(get_template_manager("coding_template").get_system_prompt())