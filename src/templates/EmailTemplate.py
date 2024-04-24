from src.templates.interface import BaseTemplate, templates, AvailableTemplates


class EmailTemplate(BaseTemplate):
    def __init__(self):
        super().__init__(
        description = "",
        persona = "",
        task = "",
        example = "",
        tools = "",
        system_prompt=[{}]
        )

def get_email_template():
    return EmailTemplate()

templates.templates[AvailableTemplates.EMAIL] = get_email_template

def main():
    return EmailTemplate()


if __name__ == "__main__":
    main()