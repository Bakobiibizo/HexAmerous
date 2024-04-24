from src.templates.interface import BaseTemplate, templates, available_templates


class SocialMediaTemplate(BaseTemplate):
    def __init__(self):
        super().__init__(
            description = "",
            persona = "",
            task = "",
            example = "",
            tools = "",
            system_prompt=[{}]
        )        

def get_social_media_template():
    return SocialMediaTemplate()

templates.templates["SocialMediaTemplate"] = get_social_media_template

def main():
    return SocialMediaTemplate()


if __name__ == "__main__":
    main()