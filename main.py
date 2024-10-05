from src.text_generators.manager import GeneratorManager
from src.templates.template_manager import TemplateManager
from src.text_generators.interface import AvailableGenerators
from src.templates.template_interface import AvailableTemplates
from src.templates.saved_templates.coding_template import CodingTemplate
from src.text_generators.ChatGPT4Generator import GPT4Generator

available_templates = AvailableTemplates(templates={"coding": CodingTemplate})
available_generators = AvailableGenerators(templates={"GPT4Generator": GPT4Generator})

hex_manager = GeneratorManager(available_generators["GPT4Generator"])
hex_manager.generator.template = available_templates["coding"]
hex_manager.generator.set_apikey
