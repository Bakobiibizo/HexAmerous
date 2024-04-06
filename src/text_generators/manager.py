from src.data_models.generators import Generator
from src.text_generators.agent_artificial_generator import AgentArtificialGenerator
from typing import Dict, List, Iterator, Callable
from loguru import logger
import os


class GeneratorManager:
    def __init__(self, name="AgentArtificial"):
        self.generators: Dict[str, Generator] = {
            "AgentArtificial": AgentArtificialGenerator
        }
        self.generator = self.generators[name]
        self.set_generator
        

    def set_generator(self, generator: str) -> bool:
        if generator in self.generators:
            self.selected_generator = self.generators[generator]
            return True
        else:
            logger.warn(f"Generator {generator} not found")
            return False

    def set_apikey(self) -> bool:
        if self.selected_generator:
            self.set_apikey = self.selected_generator.set_apikey()
            return True
        else:
            logger.warn(f"API key {self.generators[self.selected_generator]} not found")
            return False

    def set_url(self, url: str) -> bool:
        if self.selected_generator:
            self.url = self.selected_generator.
            return True
        else:
            logger.warn(f"URL {url} not found")
            return False

    def get_generator(self) -> Generator:
        return self.selected_generator
        

    async def generate(
        self,
        queries: List[str],
        template: List[str],
        context: Dict = None,
    ) -> str:
        """Generate an answer based on a List of queries and List of contexts, and includes conversational context
        @parameter: queries : List[str] - List of queries
        @parameter: context : List[str] - List of contexts
        @parameter: conversation : Dict - Conversational context
        @returns str - Answer generated by the Generator.
        """
        if context is None:
            context = {}
        return await self.selected_generator.generate(
            queries,
            template,
            self.truncate_context_items(
                context, int(self.selected_generator.context * 0.375)
            ),
        )

    async def generate_stream(
        self,
        queries: Dict[str, str],
        template: Dict[str, str],
        context: Dict = None,
    ) -> Iterator[Dict]:
        """Generate a stream of response Dicts based on a List of queries and List of contexts, and includes conversational context
        @parameter: queries : Dict[str, str] - Dict of queries
        @parameter: template : Dict[str, str] - Dict of system template prompts
        @parameter: context : List[Dict[str, str]] - Conversational context
        @returns Iterator[Dict] - Token response generated by the Generator in this format {system:TOKEN, finish_reason:stop or empty}.
        """
        if context is None:
            context = {}
        async for result in self.selected_generator.generate_stream(
            queries,
            template,
            self.truncate_context_items(
                context, int(self.selected_generator.context * 0.375)
            ),
        ):
            yield result

    def truncate_convtext_dicts(
        self, context_dicts: List[Dict[str, any]], max_tokens: int
    ) -> List[Dict[str, any]]:
        """
        Truncate a List of conversation Dictionaries to fit within a specified maximum token limit.

        @parameter context_dicts: List[Dict[str, any]] - A List of conversation Dictionaries that may contain various keys, where 'content' key is present and contains text data.
        @parameter max_tokens: int - The maximum number of tokens that the combined content of the truncated conversation Dictionaries should not exceed.

        @returns List[Dict[str, any]]: A List of conversation Dictionaries that have been truncated so that their combined content respects the max_tokens limit. The List is returned in the original order of conversation with the most recent conversation being truncated last if necessary.

        """
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        accumulated_tokens = 0
        truncated_conversation_dicts = []

        # Start with the newest conversations
        for item_Dict in reversed(context_dicts):
            item_tokens = encoding.encode(item_Dict["content"], disallowed_special=())

            # If adding the entire new item exceeds the max tokens
            if accumulated_tokens + len(item_tokens) > max_tokens:
                # Calculate how many tokens we can add from this item
                remaining_space = max_tokens - accumulated_tokens
                truncated_content = encoding.decode(item_tokens[:remaining_space])

                # Create a new truncated item Dictionary
                truncated_item_Dict = {
                    "type": item_Dict["type"],
                    "content": truncated_content,
                    "typewriter": item_Dict["typewriter"],
                }

                truncated_context_dicts.append(truncated_item_Dict)
                break

            truncated_context_dicts.append(item_Dict)
            accumulated_tokens += len(item_tokens)

        # The List has been built in reverse order so we reverse it again
        return List(reversed(truncated_context_dicts))

    def set_generator(self, generator: str) -> bool:
        if generator in self.generators:
            self.selected_generator = self.generators[generator]
            return True
        else:
            logger.warn(f"Generator {generator} not found")
            return False

    def get_generators(self) -> Dict[str, Generator]:
        return self.generators
