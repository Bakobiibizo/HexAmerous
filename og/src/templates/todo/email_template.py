"""
from src.data_models.templates import BaseTemplate


class EmailTemplate(BaseTemplate):
    def __init__(self):
        super().__init__()
        self.description = ""
        self.persona = ""
        self.task = ""
        self.tools = ""


def main():
    return EmailTemplate()


if __name__ == "__main__":
    main()
"""