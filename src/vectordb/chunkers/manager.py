"""
Chunker Manager. Manager class that handles chunking classes. Based one Weaviate's Verba.
https://github.com/weaviate/Verba
"""
import tiktoken
from loguru import logger
from typing_extensions import List, Dict

from src.vectordb.readers.document import Document
from src.vectordb.chunkers.interface import Chunker
from src.vectordb.chunkers.SentenceChunker import SentenceChunker
from src.vectordb.chunkers.TiktokenChunker import TokenChunker
from src.vectordb.chunkers.WordChunker import WordChunker


class ChunkerManager:
    """
    Chunker Manager class. Handles chunking classes.
    """
    def __init__(self):
        """
        Initializes a new instance of the ChunkerManager class.

        This method initializes the instance variables of the ChunkerManager class. It creates an empty List called `batch`, sets the `token_count` variable to 0, and creates an empty List called `batches`. It also creates a Dictionary called `chunker` with three key-value pairs, where the keys are strings representing the names of different chunking classes ("TokenChunker", "WordChunker", and "SentenceChunker"), and the values are instances of the corresponding chunking classes (`TokenChunker`, `WordChunker`, and `SentenceChunker`). The `selected_chunker` variable is then set to the instance of the `TokenChunker` class.

        Parameters:
            None

        Returns:
            None
        """
        self.batch = []
        self.token_count = 0
        self.batches = []

        self.chunker: Dict[str, Chunker] = {
            "TokenChunker": TokenChunker(),
            "WordChunker": WordChunker(),
            "SentenceChunker": SentenceChunker(),
        }
        self.selected_chunker: Chunker = self.chunker["TokenChunker"]

    def chunk(
        self, documents: List[Document], units: int, overlap: int
    ) -> List[Document]:
        """
        Chunk verba documents into chunks based on units and overlap.

        This method takes a List of Verba documents, the number of units per chunk, and the overlap between chunks. It uses the selected chunker to chunk the documents and returns a List of the chunked documents. If the chunked documents pass the check for the token count, the List of chunked documents is returned. Otherwise, an empty List is returned.

        Parameters:
            documents (List[Document]): A List of Verba documents to be chunked.
            units (int): The number of units per chunk (words, sentences, etc.).
            overlap (int): The amount of overlap between chunks.

        Returns:
            List[Document]: A List of chunked documents if the chunked documents pass the check for the token count. Otherwise, an empty List.
        """
        chunked_docs = self.selected_chunker.chunk(documents, units, overlap)
        logger.info("Chunking completed")
        return chunked_docs if self.check_chunks(chunked_docs) else []

    def set_chunker(self, chunker: str) -> bool:
        """
        Set the selected chunker based on the given chunker name.

        Parameters:
            chunker (str): The name of the chunker to be set.

        Returns:
            bool: True if the chunker is found and set successfully, False otherwise.
        """
        if chunker in self.chunker:
            self.selected_chunker = self.chunker[chunker]
            return True
        else:
            logger.warning(f"Chunker {chunker} not found")
            return False

    def get_chunkers(self) -> Dict[str, Chunker]:
        """
        Returns a Dictionary containing all the chunkers available.

        :return: A Dictionary where the keys are the names of the chunkers and the values are the chunkers themselves.
        :return type: Dict[str, Chunker]
        """
        return self.chunker

    def check_chunks(self, documents: List[Document]) -> int:
        """
        Checks the token count of chunks in a List of Verba documents.

        This function takes a List of Verba documents as input and checks the token count of each chunk in the documents. It uses the selected chunker to encode the text of each chunk and calculates the token count. The function hardcaps the token count of each chunk to 1000 tokens.

        Parameters:
            documents (List[Document]): A List of Verba documents to be checked.

        Returns:
            int: The number of batches created from the chunks in the documents. If no batches are created, 0 is returned.

        Raises:
            IndexError: If no batches are created.
        """

        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        try:
            for document in documents:
                chunks = document.chunks
                for chunk in chunks:
                    tokens = encoding.encode(chunk.text, disallowed_special=())
                    chunk.set_tokens(tokens)
                    while self.token_count <1000:
                        for token in tokens:
                            self.token_count += 1
                            self.batch.append(token)
                            if len(self.batch) >= 1000:
                                self.batch = []
                                self.token_count = 0
                                break
                            self.batches.append(self.batch)
        except IndexError as e:
            logger.error(f"no batchs created.{e}")
            return 0
        return len(self.batches)
