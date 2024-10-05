from pydantic import BaseModel, Field
from typing import List, Dict, Callable, Any, Optional
from pathlib import Path, PosixPath
from importlib import import_module
from src.data_models.generics import DynamicManager
import json
from loguru import logger


class Template(BaseModel):
    description: str
    persona: str
    task: str
    example: str
    tools: str
    system_prompt: Dict[str, str] = Field(default_factory=dict, help="The system prompt to use for the template")

class BaseTemplate(Template):
    def __init__(self, template: Template, **kwargs):
        super().__init__(**template.__dict__, **kwargs)
        self.create_system_prompt()

    def get_all_fields(self):
        """
        Returns a formatted string representing the template of the object.

        :return: A string representing the template of the object.
        :rtype: str
        """
        return f"""
Persona: {self.persona}

Task: {self.task}

Example: {self.example}

Tools: {self.tools}
"""

    def update_template(self, new_template: Template):
        self.persona = new_template.persona
        self.task = new_template.task
        self.example = new_template.example
        self.tools = new_template.tools

    def create_system_prompt(self):
        if self.system_prompt is None:
            self.system_prompt = {"role": "system", "content": self.get_template()}
        return self.system_prompt

    def create_message(self, message: str):
        return {"role": "user", "content": message}


class Manager(DynamicManager):
    def __init__(self, saved_templates_path: Path = Path("src/templates/saved_templates")):
        super().__init__(saved_templates_path=saved_templates_path)
        self.add_field("saved_templates_path", saved_templates_path)

class TemplateManager(Manager):
    saved_templates_path: Path = Path("src/templates/saved_templates")
    def __init__(self, template: Optional[BaseTemplate] = None, saved_templates_path: Path = Path("src/templates/saved_templates")):
        super().__init__(saved_templates_path=saved_templates_path)
        self.add_field("saved_templates_path", saved_templates_path)
        if template is not None:
            self.add_field("system_prompt", template.get_system_prompt())
            self.add_template(template.name, template)
        self.add_templates()
    
    def add_template(self, name: str, template: BaseTemplate):
        self.__setattr__(name, template)
        
    def remove_template(self, name: str):
        self.__delattr__(name)
        
    def update_template(self, name: str, template: BaseTemplate):
        self.__setattr__(name, template)
                         
    def get_template(self, name: str):
        return self.__getattr__(name)
    
    def get_all_templates(self):
        return self.__dict__
    
    def add_templates(self):
        logger.info(f"Adding templates from {self.saved_templates_path}")
        for template in self.saved_templates_path.glob("*.py"):
            if template.name != "__init__.py":
                module_name = f"src.templates.saved_templates.{template.stem}"
                logger.debug(f"Importing module: {module_name}")
                try:
                    module = import_module(module_name)
                    # Look for a function named get_{template_name}_template
                    getter_name = f"get_{template.stem}"
                    logger.debug(f"Checking for getter: {getter_name}")
                    if hasattr(module, getter_name):
                        getter = getattr(module, getter_name)
                        logger.debug(f"Getter found, adding template: {template.stem}")
                        self.add_field(template.stem, getter())
                    else:
                        logger.warning(f"Getter {getter_name} not found in {module_name}")
                except ImportError as e:
                    logger.error(f"Failed to import {module_name}: {e}")
                    
    def to_dict(self):
        return self.__dict__
    
    def to_json(self):
        return json.dumps(self.__dict__, indent=4, default=str)
    
    def to_model(self, input_dict: Dict):
        return Template(**input_dict)


def get_template_manager():
    return TemplateManager()

if __name__ == "__main__":
    templates = get_template_manager()
    templatedict = templates.to_json()

    print(templatedict)

