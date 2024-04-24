from src.templates.interface import BaseTemplate, templates, AvailableTemplates


class ResearchTemplate(BaseTemplate):
    def __init__(self):
        super().__init__(
            description = "",
            persona = "",
            task = "",
            example = "",
            tools = "",
            system_prompt=[{}]
        )        

def get_research_template():
    return ResearchTemplate()

templates.templates[AvailableTemplates.RESEARCH] = get_research_template

def main():
    return ResearchTemplate()


if __name__ == "__main__":
    main()