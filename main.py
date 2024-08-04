from src.text_generators.manager import GeneratorManager
from src.templates.manager import TemplateManager
from src.text_generators.interface import available_generators
from src.templates.interface import available_templates
from src.templates.coding_template import CodingTemplate
from src.text_generators.ChatGPT4Generator import GPT4Generator

available_templates.templates["coding"] = CodingTemplate
available_generators.generators["gpt4"] = GPT4Generator


class HexGenerator:
    def __init__(self):
        self.generator = GeneratorManager(
            selected_generator=""
        )
        self.template = TemplateManager()