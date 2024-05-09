"""
Retriever Manager. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""

from typing import List, Tuple, Dict
from weaviate.client import Client
from loguru import logger
from src.vectordb.retrievers.interface import Retriever
from src.vectordb.embedders.interface import Embedder
from src.vectordb.chunkers.chunk import Chunk
from src.text_generators.interface import Generator
from src.vectordb.retrievers.SimpleRetriever import SimpleRetriever
from src.vectordb.retrievers.WindowRetriever import WindowRetriever


class RetrieverManager:
    """
    RetrieverManager class for managing retrievers.

    Attributes:
        retrievers (Dict[str, Retriever]): Dictionary of retrievers.
        selected_retriever (Retriever): Selected retriever for retrieval operations.
    """

    def __init__(self):
        """
        Initializes the RetrieverManager with two retrievers, WindowRetriever and SimpleRetriever, and sets the selected retriever to WindowRetriever.
        """
        self.retrievers: Dict[str, Retriever] = {
            "WindowRetriever": WindowRetriever(),
            "SimpleRetriever": SimpleRetriever(),
        }
        self.selected_retriever: Retriever = self.retrievers["WindowRetriever"]

    def retrieve(
        self,
        queries: List[str],
        client: Client,
        embedder: Embedder,
        generator: Generator,
    ) -> Tuple[List[Chunk], str]:
        """
        Retrieves chunks and managed context using the selected retriever.

        Args:
            queries (List[str]): List of queries to retrieve chunks for.
            client (Client): Client object for making API requests.
            embedder (Embedder): Embedder object for generating embeddings.
            generator (Generator): Generator object for managing context window.

        Returns:
            Tuple[List[Chunk], str]: Tuple containing List of chunks and managed context.
        """
        chunks, context = self.selected_retriever.retrieve(queries, client, embedder)
        managed_context = self.selected_retriever.cutoff_text(
            context, generator.context_window
        )
        return chunks, managed_context

    def set_retriever(self, retriever: str) -> bool:
        """
        Set the selected retriever for retrieval operations.

        Args:
            retriever (str): The name of the retriever to set.

        Returns:
            bool: True if the retriever is found and set successfully, False otherwise.
        """
        if retriever in self.retrievers:
            self.selected_retriever = self.retrievers[retriever]
            return True
        else:
            logger.warning(f"Retriever {retriever} not found")
            return False

    def get_retrievers(self) -> Dict[str, Retriever]:
        """
        Returns the Dictionary of retrievers.
        """
        return self.retrievers
