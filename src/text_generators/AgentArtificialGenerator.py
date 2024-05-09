import os
import json
import httpx
from typing import List, Dict, Optional, Callable, Iterator
from src.text_generators.interface import (
    Generator,
    GeneratorConfig,
    available_generators,
)
from src.templates.interface import available_templates, base_template
from dotenv import load_dotenv

load_dotenv()


class AgentArtificialGenerator(Generator):
    def __init__(
        self,
        template=available_templates.templates["coding"],
        url=str(os.getenv("AGENTARTIFICIAL_URL")),
        api=str(os.getenv("AGENTARTIFICIAL_API_KEY")),
        context_window=10000,
        context=[],
        model="llama3_8b",
    ):
        """
        Initializes an instance of the AgentArtificialGenerator class.

        Args:
            template (str, optional): The template to use for generating text. Defaults to the coding template.
            url (str, optional): The URL of the AgentArtificial API. Defaults to the value of the AGENTARTIFICIAL_URL environment variable.
            api (str, optional): The API key for the AgentArtificial API. Defaults to the value of the AGENTARTIFICIAL_API_KEY environment variable.
            context_window (int, optional): The size of the context window for the model. Defaults to 10000.
            context (List[Dict[str, str]], optional): The context for the model. Defaults to an empty list.
            model (str, optional): The model to use for generating text. Defaults to "llama3_8b".

        Returns:
            None
        """
        super().__init__(
            template=template,
            url=url,
            api=api,
            context_window=context_window,
            context=context,
        )
        self.model = model
        self.client = httpx.Client()

    def set_apikey(self) -> bool:
        """
        A description of the entire function, its parameters, and its return types.

        Parameters:
            self (AgentArtificialGenerator): The instance of the AgentArtificialGenerator class.

        Returns:
            bool: True if the API key is successfully set, False otherwise.
        """
        return bool(self.api)

    def set_url(self) -> bool:
        """
        Sets the URL for the current object.

        :return: A boolean indicating whether the URL was successfully set.
        """
        return bool(self.url)

    def set_context(self) -> bool:
        """
        Sets the context for the current object.

        This method is responsible for setting the context for the current object. It should be implemented by any class that inherits from the current class.

        Returns:
            bool: True if the context is successfully set, False otherwise.
        """
        return bool(self.context)

    def set_context_window(self) -> bool:
        """
        Sets the context window for the current object.

        Returns:
            bool: True if the context window is successfully set, False otherwise.
        """
        return bool(self.context_window)

    def set_template(self) -> bool:
        """
        Sets the template for the current object.

        This method is responsible for setting the template for the current object. It should be implemented by any class that inherits from the current class.

        Returns:
            bool: True if the template is successfully set, False otherwise.
        """
        return bool(self.template)

    def set_configuration(
        self,
        template: Callable,
        url: str,
        api: str,
        context_window: int,
        context: List[Dict[str, str]],
    ):
        """
        Sets the configuration for the AgentArtificialGenerator object.

        Args:
            template (Callable): A callable object that returns a template.
            url (str): The URL of the AgentArtificial API.
            api (str): The API key for the AgentArtificial API.
            context_window (int): The size of the context window for the model.
            context (List[Dict[str, str]]): The context for the model.

        Returns:
            str: The serialized model configuration.

        Raises:
            None
        """
        return GeneratorConfig(
            template=template(),
            url=url,
            api=api,
            context_window=context_window,
            context=context,
        ).model_dump()

    def install_depenedencies(self):
        """
        Install the dependencies for the class.

        This function checks if the `httpx` module is installed and raises an `ImportError` if it is not. If `httpx` is not installed, the function uses the `os.system` function to run the command `pip install httpx` to install the module.

        Parameters:
            self: The instance of the class.

        Returns:
            None
        """
        try:
            import httpx  # type: ignore

            if not httpx:
                raise ImportError
        except ImportError:
            os.system("pip install httpx")

    def prepare_messages(
        self, queries: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for the conversation.

        Args:
            queries (Optional[List[str]]): A list of queries to be added to the conversation context.

        Returns:
            List[Dict[str, str]]: A list of messages in the format {"role": str, "content": str}.
        """

        if not self.context:
            self.context = [self.template.create_system_prompt()]  # type: ignore
        if not queries:
            return self.context
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            self.context.append(base_template.create_message(query))
        if queries:
            for query in queries:
                self.context.append({"role": "user", "content": query})
        return self.context

    def prepare_body(self):
        """
        Prepares the body of the request to be sent to the AgentArtificial API.

        Returns:
            dict: A dictionary containing the model and messages to be sent.
                - model (str): The model to be used for generating the response.
                - messages (List[Dict[str, str]]): The list of messages in the format {"role": str, "content": str}.
        """
        return {"model": self.model, "messages": self.context}

    def generate(self, queries, url):
        """
        Generates a response using the given queries and sends a POST request to the specified URL.

        Args:
            queries (List[str]): The list of queries to generate a response for.
            url (str): The URL to send the POST request to.

        Returns:
            dict: The JSON response from the API.
        """
        self.prepare_messages(queries=queries)
        body = self.prepare_body()
        response = self.client.post(url, json=json.dumps(body))
        return response.json()

    async def generate_stream(
        self, messages, url="the-roost- agentartificial.ngrok.dev", model="codellama"
    ):
        """
        Asynchronously generates a stream of responses using the given messages and sends a POST request to the specified URL.

        Args:
            messages (List[Dict[str, str]]): The list of messages in the format {"role": str, "content": str}.
            url (str, optional): The URL to send the POST request to. Defaults to "the-roost-agentartificial.ngrok.dev".
            model (str, optional): The model to be used for generating the response. Defaults to "codellama".

        Yields:
            bytes: The stream of response data.

        Raises:
            None
        """

        payload = {"messages": messages, "model": model, "streaming": True}
        headers = {
            "Authorization": f"Bearer {self.api}",
            "Content-Type": "application/json",
        }
        res = self.client.post(url, data=payload, headers=headers)
        yield res.read()


def get_agentartificial_generator():
    """
    Returns an instance of the AgentArtificialGenerator class.

    This function creates and returns an instance of the AgentArtificialGenerator class. The instance can be used to generate text using the AgentArtificial API.

    Returns:
        AgentArtificialGenerator: An instance of the AgentArtificialGenerator class.
    """
    return AgentArtificialGenerator()


def get_agentartficial_generator():
    return AgentArtificialGenerator()


available_generators.add_generator("agent_artificial", get_agentartificial_generator)
