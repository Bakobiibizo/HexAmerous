from src.text_generators.manager import manager as generator_manager
from src.text_generators.manager import generator_map
from src.templates import manager as template_manager


def init_generator(selected_generator: str):
    GeneratorManager = generator_manager(
        selected_generator=generator_map["agent_artificial"]
)

