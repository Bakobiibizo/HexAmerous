"""
WordChunker for vectorstore. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""

import spacy
from tqdm import tqdm
from loguru import logger
from typing_extensions import List

from src.vectordb.readers.document import Document
from src.vectordb.chunkers.chunk import Chunk
from src.vectordb.chunkers.interface import Chunker


class WordChunker(Chunker):
    """
    WordChunker for Verba built with spaCy.
    """

    def __init__(self, name, requires_library, requires_env, description):
        """
        Initializes the WordChunker object.

        This method initializes the WordChunker object by calling the __init__ method of the parent class using the super() function. It sets the `name` attribute to "WordChunker", `requires_library` to ["spacy"], `default_units` to 100, `default_overlap` to 50, `description` to "Chunk documents by words. You can specify how many words should overlap between chunks to improve retrieval." It then tries to set the `nlp` attribute to a blank spacy model for English, and if Spacy is not installed, it sets `nlp` to None.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__(
            name=name,
            requires_library=requires_library,
            requires_env=requires_env,
            description=description,
        )
        self.name = "WordChunker"
        self.requires_library = ["spacy"]
        self.default_units = 100
        self.default_overlap = 50
        self.description = "Chunk documents by words. You can specify how many words should overlap between chunks to improve retrieval."
        try:
            self.nlp = spacy.blank("en")
        except ValueError as e:
            logger.warning(f"Spacy is not installed. Setting nlp to none. {e}")
        self.nlp = None

    def chunk(
        self, documents: List[Document], units: int, overlap: int
    ) -> List[Document]:
        """
        Chunk the given List of documents into smaller chunks based on the specified units and overlap.

        Args:
            documents (List[Document]): A List of Document objects representing the documents to be chunked.
            units (int): The number of words per chunk.
            overlap (int): The number of words that should overlap between chunks.

        Returns:
            List[Document]: The List of Document objects with their chunks added.

        Description:
            This function takes a List of Document objects and chunks them into smaller chunks based on the specified units and overlap.
            Each Document object is checked to see if it already has chunks. If it does, the function skips it.
            If the Document does not have chunks, the function uses the `nlp` attribute (a spacy model) to tokenize the text of the document.
            If the number of tokens in the document is less than or equal to the specified units, a single chunk is created with the entire text of the document.
            If the overlap is greater than or equal to the units, a warning is logged and the function continues to the next document.
            The function then iterates over the tokens, creating chunks of the specified units and overlapping them by the specified overlap.
            Each chunk is created by creating a Chunk object with the corresponding text, document name, document type, and a unique chunk ID.
            The function then appends the Chunk object to the Document object's List of chunks.
            The function returns the List of Document objects with their chunks added.
        """
        for document in tqdm(
            documents, total=len(documents), desc="Chunking documents"
        ):
            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            if not document:
                raise ValueError("Document is empty")

            if self.nlp:
                doc = self.nlp(document.text or " document")

            if units > len(doc) or units < 1:
                doc_chunk = Chunk(
                    text=doc.text,
                    doc_name=document.name or "document",
                    doc_type=document.doc_type or "document",
                    chunk_id=str(0),
                )

            if overlap >= units:
                logger.warning(
                    f"Overlap value is greater than unit (Units {units}/ Overlap {overlap})"
                )
                continue

            i = 0
            split_id_counter = 0
            while i < len(doc):
                # Overlap
                start_i = i
                end_i = i + units
                end_i = min(end_i, len(doc))
                doc_chunk = Chunk(
                    text=doc[start_i:end_i].text,
                    doc_name=document.name or "document",
                    doc_type=document.doc_type or "document",
                    chunk_id=str(split_id_counter) or str(0),
                )
                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(doc):
                    break

                i += units - overlap  # Step forward, considering overlap

        return documents
