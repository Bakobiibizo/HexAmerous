"""
Cohere Embedder. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""

from weaviate.client import Client
from typing_extensions import List

from src.vectordb.embedders.interface import Embedder
from src.vectordb.readers.document import Document


class CohereEmbedder(Embedder):
    """
    CohereEmbedder for Verba.
    """

    def __init__(self):
        """
        Initializes a new instance of the class.

        This method initializes the CohereEmbedder class with the necessary parameters for embedding and retrieving
        objects using Cohere's ember multilingual-v2.0 model. It sets the description, name, requires_env, and
        requires_library attributes. The requires_env attribute is set to a list containing the "COHERE_API_KEY"
        environment variable, while the requires_library attribute is set to None. The vectorizer attribute is set
        to "text2vec-cohere".

        Parameters:
            None

        Returns:
            None
        """
        super().__init__(
            description=(
                "Embeds and retrieves objects using Cohere's ember multilingual-v2.0 model"
            ),
            name="CohereEmbedder",
            requires_env=["COHERE_API_KEY"],
            requires_library=None,
        )
        self.vectorizer = "text2vec-cohere"
        self.tokenizer = CohereEmbedder()

    def embed(
        self, documents: List[Document], client: Client, batch_size: int = 100
    ) -> bool:
        """
        Embeds the given list of documents and their chunks into Weaviate using the SentenceTransformer model.

        Parameters:
            documents (List[Document]): A list of Document objects representing the documents to be embedded.
            client (Client): The Weaviate client used to import the embedded data.
            batch_size (int, optional): The batch size for embedding the documents. Defaults to 100.

        Returns:
            bool: True if the embedding and import were successful, False otherwise.
        """
        return self.tokenizer.embed(documents, client)
