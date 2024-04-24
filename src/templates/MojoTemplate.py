from src.templates.interface import BaseTemplate, templates, available_templates


class MojoTemplate(BaseTemplate):
    def __init__(self):
        """
        Initializes a new instance of the MojoTemplate class.

        This function sets up the initial state of the MojoTemplate object by calling the __init__ method of the BaseTemplate class and setting the values of the description, persona, task, example, and tools attributes. It also sets the value of the system_prompt attribute by calling the create_system_prompt method.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__(
            description="An expert mojo developer",
            persona="You are a expert developer. You have indepth knowledge of python and typescript along with supporting frameworks. You have been given the documents of a new programing language called Mojo(also know as modular), its kept in your vectorstore. You are helping out Richard with learning this new super set of python. You are careful to reference your answers against the documents in your vectorstore.",
            task="You provide verbose detailed and comprehensive answers to questions. You make sure to go through your answers carefully step by step to ensure the information is correct.",
            example="",
            tools="",
            system_prompt=self.create_system_prompt()
        )


def main():
    """
    Initializes and returns a new instance of the MojoTemplate class.

    This function creates and returns a new instance of the MojoTemplate class, which represents a template for generating Mojo-related content. The MojoTemplate class is responsible for setting up the initial state of the template by calling the __init__ method of the BaseTemplate class and setting the values of the description, persona, task, example, and tools attributes. It also sets the value of the system_prompt attribute by calling the create_system_prompt method.

    Returns:
        MojoTemplate: A new instance of the MojoTemplate class.
    """
    return MojoTemplate()

def get_mojo_template():
    return MojoTemplate()

templates.templates["MojoTemplate"] = get_mojo_template

if __name__ == "__main__":
    main()