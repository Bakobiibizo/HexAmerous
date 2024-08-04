from pydantic import BaseModel
from typing_extensions import List, Dict, Iterator, Callable
from abc import ABC, abstractmethod


class Generator(BaseModel, ABC):
    template: Callable
    url: str
    api: str
    context: List
    context_window: int

    @abstractmethod
    def set_apikey(self) -> bool:
        """
        Sets the API key for the Generator.

        This method is responsible for setting the API key for the Generator. It should be implemented by any class that inherits from the Generator class.

        Returns:
            bool: True if the API key is successfully set, False otherwise.
        """

    @abstractmethod
    def set_url(self) -> bool:
        """
        Sets the URL for the current object.

        :return: A boolean indicating whether the URL was successfully set.
        """

    @abstractmethod
    def set_context(self) -> bool:
        """
        Sets the context for the current object.

        This method is responsible for setting the context for the current object. It should be implemented by any class that inherits from the current class.

        Returns:
            bool: True if the context is successfully set, False otherwise.
        """
    
    @abstractmethod
    def set_context_window(self) -> bool:
        """
        Sets the context window for the current object.

        This method is responsible for setting the context window for the current object. It should be implemented by any class that inherits from the current class.

        Returns:
            bool: True if the context window is successfully set, False otherwise.
        """

    @abstractmethod
    def set_template(self) -> bool:
        """
        A description of the entire function, its parameters, and its return types.
        """

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Asynchronously generates a response based on a list of messages.

        Args:
            messages (List[Dict[str, str]]): A list of dictionaries representing messages.

        Returns:
            Dict[str, str]: A dictionary representing the generated response.
        """
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> Iterator[Dict[str, str]]:
        """
        Asynchronously generates a stream of response dictionaries based on a list of messages.

        Args:
            messages (List[Dict[str, str]]): A list of dictionaries representing messages.

        Yields:
            Iterator[Dict[str, str]]: An iterator that yields dictionaries representing the generated responses.
        """

    @abstractmethod
    def prepare_messages(
        self,
        queries: List[str],
        context: List[Dict[str, str]],
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        A description of the entire function, its parameters, and its return types.
        """
        

class GeneratorConfig(BaseModel):
    template: Callable
    url: str
    api: str
    context: List
    context_window: int


class AvailableGenerators(BaseModel):
    generators: Dict[str, Callable] = {}

    def add_generator(self, name: str, generator):
        """
        Add a new generator to the AvailableGenerators instance.

        Args:
            name (str): The name of the generator to add.
            generator (Callable): The generator function to add.

        Returns:
            None
        """
        self.generators[name] = generator

    def remove_generator(self, name: str):
        """
        Remove a generator from the AvailableGenerators instance.

        Args:
            name (str): The name of the generator to remove.

        Returns:
            None
        """
        del self.generators[name]

    def get_generator(self, name: str) -> Callable:
        """
        Retrieves a generator function by name.

        Args:
            name (str): The name of the generator to retrieve.

        Returns:
            Callable: The generator function associated with the provided name.
        """
        return self.generators[name]

    def get_all_generators(self) -> Dict[str, Callable]:
        """
        Returns a dictionary containing all the generators available.

        :return: A dictionary where the keys are the names of the generators and the values are the callable functions.
        :rtype: Dict[str, Callable]
        """
        return self.generators

    def get_generator_names(self) -> List[str]:
        """
        Returns a list of names of all available generators.

        :return: A list of strings representing the names of the generators.
        :rtype: List[str]
        """
        return list(self.generators.keys())

    def get_generator_by_name(self, name: str) -> Generator:
        """
        Retrieves a generator function by name.

        Args:
            name (str): The name of the generator to retrieve.

        Returns:
            Generator: The generator function associated with the provided name.
        """
        return self.generators[name]()


available_generators = AvailableGenerators()