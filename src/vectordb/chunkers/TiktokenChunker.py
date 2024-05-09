"""
Tiktoken Token Chunker. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""

import tiktoken
from tqdm import tqdm
from loguru import logger
from typing_extensions import List

from src.vectordb.chunkers.interface import Chunker
from src.vectordb.chunkers.chunk import Document, Chunk


class TokenChunker(Chunker):
    """
    TokenChunker built with tiktoken.
    """

    def __init__(self, name, requires_library, requires_env, description):
        """
        Initializes the TokenChunker class.

        This method initializes the TokenChunker class by calling the __init__ method of the parent class using the super() function. It sets the 'name' attribute to "TokenChunker", the 'requires_library' attribute to ["tiktoken"], the 'default_units' attribute to 250, and the 'default_overlap' attribute to 50. It also sets the 'description' attribute to "Chunk documents by tokens powered by tiktoken. You can specify how many tokens should overlap between chunks to improve retrieval." Finally, it sets the 'encoding' attribute to the encoding for the "gpt-3.5-turbo" model using the tiktoken library.

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
        self.name = "TokenChunker"
        self.requires_library = ["tiktoken"]
        self.default_units = 250
        self.default_overlap = 50
        self.description = "Chunk documents by tokens powered by tiktoken. You can specify how many tokens should overlap between chunks to improve retrieval."
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def chunk(
        self, documents: List[Document], units: int, overlap: int
    ) -> List[Document]:
        """
        Chunk the given List of documents into smaller chunks based on the specified units and overlap.

        Args:
            documents (List[Document]): A List of Document objects representing the documents to be chunked.
            units (int): The number of tokens per chunk.
            overlap (int): The number of tokens that should overlap between chunks.

        Returns:
            List[Document]: The List of Document objects with their chunks added.

        Raises:
            None

        Description:
            This function takes a List of Document objects and chunks them into smaller chunks based on the specified units and overlap.
            Each Document object is checked to see if it already has chunks. If it does, the function skips it.
            If the Document does not have chunks, the function encodes the text of the document using the tiktoken encoding.
            If the number of tokens in the encoded text is less than or equal to the specified units, a single chunk is created with the entire text of the document.
            If the overlap is greater than or equal to the units, a warning is logged and the function continues to the next document.
            The function then iterates over the encoded tokens, creating chunks of the specified units and overlapping them by the specified overlap.
            Each chunk is created by decoding the corresponding tokens using the tiktoken encoding and creating a Chunk object with the decoded text, document name, document type, and a unique chunk ID.
            The function then appends the Chunk object to the Document object's List of chunks.
            The function returns the List of Document objects with their chunks added.
        """
        for document in tqdm(
            documents, total=len(documents), desc="Chunking documents"
        ):
            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            encoded_tokens = self.encoding.encode(document.text, disallowed_special=())

            if units > len(encoded_tokens) or units < 1:
                doc_chunk = Chunk(
                    text=document.text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=0,
                )

            if overlap >= units:
                logger.warning(
                    f"Overlap value is greater than unit (Units {units}/ Overlap {overlap})"
                )
                continue

            i = 0
            split_id_counter = 0
            while i < len(encoded_tokens):
                # Overlap
                start_i = i
                end_i = min(i + units, len(encoded_tokens))

                chunk_tokens = encoded_tokens[start_i:end_i]
                chunk_text = self.encoding.decode(chunk_tokens)

                doc_chunk = Chunk(
                    text=chunk_text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=str(split_id_counter),
                )
                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(encoded_tokens):
                    break

                i += units - overlap  # Step forward, considering overlap

        return documents
