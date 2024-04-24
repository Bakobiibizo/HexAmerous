from src.text_generators.manager import GeneratorManager
from src.templates.manager import TemplateManager



class HexGenerator:
    def __init__(self, selected_template: str, selected_generator: str):
        self.generator = GeneratorManager(
            selected_generator
        )
        self.template = TemplateManager(selected_template)