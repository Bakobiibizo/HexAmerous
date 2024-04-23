"""
ADAEmbedder. Based on Weaviate's Verba.
"""
import os
import openai
from weaviate.client import Client
from typing_extensions import List
from dotenv import load_dotenv

from src.vectordb.embedders.interface import Embedder
from src.vectordb.readers.document import Document

load_dotenv()

class ADAEmbedder(Embedder):
    """
    ADAEmbedder for Verba.
    """
    def __init__(self) -> None:
        """
        Constructor for ADAEmbedder class. Initializes the name, required environment variables,
        required libraries, and description for the embedder. Sets the vectorizer to 'text2vec-openai'.
        """
        super().__init__(
            name="ADAEmbedder",
            requires_env=["OPENAI_API_KEY"],
            requires_library=["openai"],
            description="Embeds and retrieves objects using OpenAI's ADA model",
        )
        self.vectorizer = "text2vec-openai"
        self.openai = openai.OpenAI()
        self.openai.api_key = str(os.getenv("OPENAI_API_KEY"))

    def embed(
        self,
        documents: List[Document],
        client: Client,
        batch_size: int = 100
    ) -> bool:
        """
        Embeds the given list of documents and their chunks into Weaviate using the SentenceTransformer model.
        Parameters:
            documents (List[Document]): A list of Document objects representing the documents to be embedded.
            client (Client): The Weaviate client used to import the embedded data.
        Returns:
            bool
        """
        return self.import_data(documents, client)
    
    def vectorize_query(self, query: str):
        return self.openai.embeddings.create(input=[query], model="text-embedding-ada-002")