<<<<<<< Updated upstream
from src.vectordb.xml_loader import sitemap_loader


def main():
    sitemap_loader()

if __name__=="__main__":
    main()
=======
from src.text_generators.manager import GeneratorManager
from src.templates.manager import TemplateManager
from src.text_generators.interface import available_generators
from src.templates.interface import available_templates
from src.templates.CodingTemplate import get_coding_template
from src.templates.EmailTemplate import get_email_template
from src.templates.KitScriptTemplate import get_scriptkit_template
from src.templates.MojoTemplate import get_mojo_template
from src.templates.ResearchTemplate import get_research_template
from src.templates.SocialMediaTemplate import get_social_media_template
from src.templates.WritingTemplate import get_writing_template
from src.text_generators.AgentArtificialGenerator import get_agentartficial_generator
from src.text_generators.AnthropicGenertor import get_anthropic_generator
from src.text_generators.HuggingFaceGenerator import get_huggingface_generator
from src.text_generators.JippityGenerator import get_jippity_generator

available_templates.templates["coding"] = get_coding_template
available_templates.templates["email"] = get_email_template
available_templates.templates["scriptkit"] = get_scriptkit_template
available_templates.templates["mojo"] = get_mojo_template
available_templates.templates["research"] = get_research_template
available_templates.templates["socialmedia"] = get_social_media_template
available_templates.templates["writing"] = get_writing_template
available_generators.generators["agentartificial"] = get_agentartficial_generator
available_generators.generators["anthropic"] = get_anthropic_generator
available_generators.generators["huggingface"] = get_huggingface_generator
available_generators.generators["jippity"] = get_jippity_generator



class HexGenerator:
    def __init__(self):
        self.generator = GeneratorManager(
            selected_generator=""
        )
        self.template = TemplateManager()
>>>>>>> Stashed changes
