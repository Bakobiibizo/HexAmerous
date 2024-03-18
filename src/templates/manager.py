"""
Template Manager
"""
from typing import List, Union
from src.data_models.templates import BaseTemplate, AvailableTemplates, Templates
from src.templates.coding_template import CodingTemplate


class TemplateManager(Templates):
    """
    Initialize the class with a selected template. 

    Parameters:
        selected_template (Union[str, AvailableTemplates]): The selected template, which can be a string or an AvailableTemplates enum value.
        
    Returns:
        None
    """
    def __init__(self, selected_template: Union[str, AvailableTemplates]):
        super().__init__()
        # TODO: Add more templates
        # This object holds a dictionary of available template names as enum values and their corresponding template classes.
        self.templates = {
            AvailableTemplates.CODING: CodingTemplate
        }
        # Set the selected template class
        self.selected_template = self.select_template(selected_template)
        # Set the system prompt
        self.template = self.get_prompt_template()
        
    
    def update_templates(
        self,
        name: str,
        new_template: "BaseTemplate"
    ) -> BaseTemplate:
        """
        Update the templates dictionary with a new template under the given name.
        
        Args:
            name (str): The name under which the new template should be stored.
            new_template (BaseTemplate): The new template object to be added.
        
        Returns:
            BaseTemplate: The newly added template.
        """
        self.templates[name] = new_template
        self.selected_template = self.select_template(name)
        return self.templates[name]

    def select_template(self, name: str) -> BaseTemplate:
        """
        Selects a template based on the given name.

        Args:
            name (str): The name of the template to select.

        Returns:
            BaseTemplate: The selected template.
        """
        self.selected_template = self.templates[name]()
        return self.selected_template

    def get_prompt_template(self) -> BaseTemplate:
        """
        Get the template and return a system prompt based on the selected template.

        Parameters:
            self: The object instance
        Returns:
            BaseTemplate: The system prompt based on the selected template
        """
        return self.selected_template.create_system_prompt()

    def list_templates(self) -> List[str]:
        """
        Return a list of all available templates.
        """
        return self.available_templates.values()