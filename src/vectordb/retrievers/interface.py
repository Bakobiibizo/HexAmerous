import tiktoken
from loguru import logger
from weaviate.client import Client
from typing_extensions import List, Tuple

from src.vectordb.component import Component
from src.vectordb.chunkers.chunk import Chunk
from src.vectordb.embedders.interface import Embedder


class Retriever(Component):
    """
    Retriever interface for retrieving data from Weaviate.
    """

    def __init__(
        self,
        name: str,
        requires_env: List[str],
        requires_library: List[str],
        description: str,
    ) -> None:
        """
        Initializes a new instance of the class.
        """
        super().__init__(
            description=description,
            name=name,
            requires_env=requires_env,
            requires_library=requires_library,
        )

    def retrieve(
        self,
        queries: List[str],
        client: Client,
        embedder: Embedder,
    ) -> Tuple[List[Chunk], str]:
        """
        Retrieve data from Weaviate using the given queries, client, and embedder.

        Args:
            queries (List[str]): A List of queries to retrieve data from Weaviate.
            client (Client): The Weaviate client used to interact with the Weaviate server.
            embedder (Embedder): The embedder used to embed the retrieved data.

        Returns:
            Tuple[List[Chunk], str]: A Tuple containing a List of retrieved chunks and the context string.

        Raises:
            NotImplementedError: If the load method is not implemented by a subclass.
        """

        raise NotImplementedError("load method must be implemented by a subclass.")

    def sort_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Sorts a List of chunks based on the doc_uuid and chunk_id.

        Args:
            chunks (List[Chunk]): A List of Chunk objects to be sorted.

        Returns:
            List[Chunk]: A sorted List of Chunk objects.
        """
        return sorted(chunks, key=lambda chunk: (chunk.doc_uuid, int(chunk.chunk_id)))

    def cutoff_text(self, text: str, content_length: int) -> str:
        """
        Cuts off the input text to a specified content length in tokens.

        Args:
            text (str): The input text to be cut off.
            content_length (int): The maximum number of tokens in the output text.

        Returns:
            str: The cut off text if the input text exceeds the content length, otherwise the input text.

        Raises:
            None

        Example:
            cutoff_text("This is a long text that needs to be cut off.", 10)
            # Output: "This is a long t..."
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        # Tokenize the input text
        encoded_tokens = encoding.encode(text, disallowed_special=())

        # Check if we need to truncate
        if len(encoded_tokens) > content_length:
            encoded_tokens = encoded_tokens[:content_length]
            truncated_text = encoding.decode(encoded_tokens)
            logger.info(f"Truncated Context to {content_length} tokens")
            return truncated_text
        else:
            logger.info(f"Retrieved Context of {len(encoded_tokens)} tokens")
            return text
