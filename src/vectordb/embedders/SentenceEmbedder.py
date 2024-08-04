"""
Mini LM Embedder. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
import torch
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer
from typing import List
from weaviate.client import Client
from loguru import logger

from src.vectordb.readers.document import Document
from src.vectordb.embedders.interface import Embedder


class MiniLMEmbedder(Embedder):
    """
    MiniLMEmbedder for Verba.
    """

    model = AutoModel
    tokenizer = AutoTokenizer

    def __init__(self):
        """
        Initializes the MiniLMEmbedder class.

        This function initializes the MiniLMEmbedder class by setting the name, required libraries, description, and vectorizer attributes. It also attempts to get the device on which the model will be run. If a CUDA-enabled GPU is available, it uses that device. If not, it checks if the Multi-Process Service (MPS) is available and uses that device. If neither a CUDA device nor an MPS device is available, it falls back to using the CPU.

        The function then loads the pre-trained model and tokenizer from the "sentence-transformers/all-MiniLM-L6-v2" repository using the AutoModel and AutoTokenizer classes from the transformers library. The model and tokenizer are moved to the device obtained earlier.

        If there is a RuntimeError during the initialization process, a warning message is logged.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.name = "MiniLMEmbedder"
        self.requires_library = ["torch", "transformers"]
        self.description = "Embeds and retrieves objects using SentenceTransformer's all-MiniLM-L6-v2 model"
        self.vectorizer = "MiniLM"
        try:

            def get_device():
                """
                Returns the appropriate device for running the model based on the availability of CUDA-enabled GPUs and Multi-Process Service (MPS).

                :return: A torch.device object representing the device to be used for running the model.
                :rtype: torch.device
                """
                if torch.cuda.is_available():
                    return torch.device("cuda")
                elif torch.backends.mps.is_available():
                    return torch.device("mps")
                else:
                    return torch.device("cpu")

            self.device = get_device()

            self.model = AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2", device_map=self.device
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2", device_map=self.device
            )
            self.model = self.model.to(self.device)

        except RuntimeError as e:
            logger.warning(str(e))

    def embed(
        self,
        documents: List[Document],
        client: Client,
    ) -> bool:
        """
        Embeds the given list of documents and their chunks into Weaviate using the SentenceTransformer model.

        Parameters:
            documents (List[Document]): A list of Document objects representing the documents to be embedded.
            client (Client): The Weaviate client used to import the embedded data.

        Returns:
            bool: True if the embedding and import were successful, False otherwise.
        """
        for document in tqdm(
            documents, total=len(documents), desc="Vectorizing document chunks"
        ):
            for chunk in document.chunks:
                chunk.set_vector(self.vectorize_chunk(chunk.text))

        return self.import_data(documents, client)

    def vectorize_chunk(self, chunk) -> List[float]:
        """
        Vectorize a chunk of text into a list of floats representing the average embedding of the tokens in the chunk.

        Parameters:
            chunk (str): The text chunk to be vectorized.

        Returns:
            List[float]: A list of floats representing the average embedding of the tokens in the chunk.

        Raises:
            RuntimeError: If there is an error creating the embeddings.
        """
        try:
            text = chunk
            tokens = self.tokenizer.tokenize(text)
            max_length = (
                self.tokenizer.model_max_length
            )  # Get the max sequence length for the model
            batches = []
            batch = []
            token_count = 0

            for token in tokens:
                token_length = len(
                    self.tokenizer.encode(token, add_special_tokens=False)
                )
                if token_count + token_length <= max_length:
                    batch.append(token)
                else:
                    batches.append(" ".join(batch))
                    batch = [token]
                    token_count = token_length

            # Don't forget to add the last batch
            if batch:
                batches.append(" ".join(batch))

            embeddings = []

            for batch in batches:
                inputs = self.tokenizer(
                    text=batch, return_tensors="pt", padding=True, truncation=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.model(**inputs)
                # Taking the mean of the hidden states to obtain an embedding for the batch
                embedding = outputs.last_hidden_state.mean(dim=1)
                embeddings.append(embedding)

            # Concatenate the embeddings to make averaging easier
            all_embeddings = torch.cat(embeddings)

            averaged_embedding = all_embeddings.mean(dim=0)

            return averaged_embedding.tolist()
        except Exception as e:
            raise RuntimeError(f"Error creating embeddings: {e}") from e

    def vectorize_query(self, query: str) -> List[float]:
        """
        Vectorize a query by calling the vectorize_chunk method and return the resulting vector.

        Parameters:
            query (str): The query to be vectorized.

        Returns:
            List[float]: A list of floats representing the vectorized query.
        """
        return self.vectorize_chunk(query)
