"""
Embedding Manager for handling the Embedder classes. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
from weaviate.client import Client
from typing import List
from loguru import logger

from typing_extensions import Dict
from src.vectordb.embedders.interface import Embedder
from src.vectordb.readers.document import Document
from src.vectordb.embedders.ADAEmbedder import ADAEmbedder
from src.vectordb.embedders.CohereEmbedder import CohereEmbedder
from src.vectordb.embedders.SentenceEmbedder import SentenceEmbedder
from src.vectordb.embedders.MiniLMEmebdder import MiniLMEmbedder


class EmbeddingManager:
    """
    Embedding Manager for handling embedder classes.
    """

    def __init__(self):
        """
        Constructor for EmbeddingManager class. Initializes the embedders dictionary with different Embedder instances and sets the selected embedder to ADAEmbedder by default.
        """
        self.embedders: Dict[str, Embedder] = {
            "MiniLMEmbedder": MiniLMEmbedder(),
            "ADAEmbedder": ADAEmbedder(),
            "CohereEmbedder": CohereEmbedder(),
            "SentenceEmbedder": SentenceEmbedder(),
        }
        self.selected_embedder: Embedder = self.embedders["ADAEmbedder"]

    def embed(
        self, documents: List[Document], client: Client, batch_size: int = 100
    ) -> bool:
        """
        Embeds a list of Verba documents and its chunks to Weaviate.

        Args:
            documents (List[Document]): List of Verba documents to be embedded.
            client (Client): Weaviate client used for embedding.
            batch_size (int, optional): Batch size of the input. Defaults to 100.

        Returns:
            bool: True if the embedding was successful, False otherwise.
        """
        return self.selected_embedder.embed(documents, client, batch_size)

    def set_embedder(self, embedder: str) -> bool:
        """
        Sets the selected embedder for embedding documents and chunks to Weaviate.

        Args:
            embedder (str): The name of the embedder to set.

        Returns:
            bool: True if the embedder is found and set successfully, False otherwise.
        """
        if embedder in self.embedders:
            self.selected_embedder = self.embedders[embedder]
            return True
        else:
            logger.warning(f"Embedder {embedder} not found")
            return False

    def get_embedders(self) -> Dict[str, Embedder]:
        """
        Get the dictionary of embedders.

        Returns:
            Dict[str, Embedder]: A dictionary where the keys are strings representing the names of the embedders and the values are instances of the Embedder class.
        """
        return self.embedders
