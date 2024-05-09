from src.text_generators.interface import Generator, available_generators
from typing import Dict, List


class GeneratorManager:
    def __init__(self, selected_generator: str):
        """
        Initializes a new instance of the GeneratorManager class.

        Args:
            selected_generator (str): The name of the selected generator.

        Returns:
            None
        """
        self.selected_generator = selected_generator
        self.generators = available_generators.generators
        self.accumulated_tokens = 0
        self.truncated_dicts = []

    def set_generator(self, generator_name: str, generator) -> Generator:
        """
        Sets the generator based on the provided generator_name.

        Args:
            generator_name (str): The name of the generator to set.

        Returns:
            Generator: The generator that is set.
        """
        print(self.generators)
        self.generator = generator
        return self.generator

    def get_generators(self) -> List[str]:
        """
        Returns a list of generator names.

        :return: A list of strings representing the names of the available generators.
        :rtype: List[str]
        """
        return list(self.generators.keys())

    def truncate_convtext_dicts(
        self, context_dicts: List[Dict[str, str]], max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Truncates a list of conversation dictionaries to a maximum number of tokens.

        Args:
            context_dicts (List[Dict[str, str]]): A list of dictionaries representing conversations,
                where each dictionary has keys "type", "content", and "typewriter".
            max_tokens (int): The maximum number of tokens allowed for the truncated conversations.

        Returns:
            List[Dict[str, str]]: A list of dictionaries representing truncated conversations.
                Each dictionary has keys "type", "content", and "typewriter".

        """
        import tiktoken

        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        # Start with the newest conversations
        for item_dict in reversed(context_dicts):
            item_tokens = encoding.encode(item_dict["content"], disallowed_special=())

            # If adding the entire new item exceeds the max tokens
            if self.accumulated_tokens + len(item_tokens) > max_tokens:
                # Calculate how many tokens we can add from this item
                remaining_space = max_tokens - self.accumulated_tokens
                truncated_content = encoding.decode(item_tokens[:remaining_space])

                # Create a new truncated item Dictionary
                truncated_item_dict = {
                    "type": item_dict["type"],
                    "content": truncated_content,
                    "typewriter": item_dict["typewriter"],
                }

                self.truncated_dicts.append(truncated_item_dict)
                break

            self.truncated_dicts.append(item_dict)
            self.accumulated_tokens += len(item_tokens)

        # The List has been built in reverse order so we reverse it again
        return list(reversed(self.truncated_dicts))
