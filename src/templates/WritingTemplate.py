from src.templates.interface import BaseTemplate, templates, available_templates


class WritingTemplate(BaseTemplate):
    def __init__(self):
        super().__init__(
            description="",
            persona="",
            task="",
            example="",
            tools="",
            system_prompt=[{}],
        )


def get_writing_template():
    return WritingTemplate()


templates.templates["WritingTemplate"] = get_writing_template


def main():
    return WritingTemplate()


if __name__ == "__main__":
    main()
