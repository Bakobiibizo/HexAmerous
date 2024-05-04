from src.data_models.templates import BaseTemplate


class WritingTemplate(BaseTemplate):
    def __init__(self):
        super().__init__()
        self.description = ""
        self.persona = ""
        self.task = ""
        self.tools = ""


def main():
    return WritingTemplate()


if __name__ == "__main__":
    main()