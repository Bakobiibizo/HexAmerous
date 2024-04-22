"""
Sentence chunker. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
import spacy
from tqdm import tqdm
from loguru import logger

from vectordb.documents.documents import Document, Chunk
from vectordb.chunkers.interface import Chunker


class SentenceChunker(Chunker):
    """
    SentenceChunker for Verba built with spaCy.
    """

    def __init__(self):
        """
        Initializes the SentenceChunker object.

        This method initializes the SentenceChunker object by calling the __init__ method of the parent class using the super() function. It sets the `name` attribute to "WordChunker", `requires_library` to ["spacy"], `default_units` to 3, `default_overlap` to 2, and `description` to "Chunk documents by sentences. You can specify how many sentences should overlap between chunks to improve retrieval." It then tries to set the `nlp` attribute to a blank spacy model for English with the "sentencizer" pipeline added, and if Spacy is not installed, it sets `nlp` to None.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.name = "WordChunker"
        self.requires_library = ["spacy"]
        self.default_units = 3
        self.default_overlap = 2
        self.description = "Chunk documents by sentences. You can specify how many sentences should overlap between chunks to improve retrieval."
        try:
            self.nlp = spacy.blank("en")
            self.nlp.add_pipe("sentencizer")
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
            units (int): The number of tokens per chunk.
            overlap (int): The number of tokens that should overlap between chunks.

        Returns:
            List[Document]: The List of Document objects with their chunks added.
        """
        for document in tqdm(
            documents, total=len(documents), desc="Chunking documents"
        ):
            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue
            if not self.nlp:
                continue
            doc = list(self.nlp(document.text).sents)

            if units > len(doc) or units < 1:
                logger.warning(
                    f"Unit value either exceeds length of actual document or is below 1 ({units}/{len(doc)})"
                )
                continue

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
                text = "".join(sent.text for sent in doc[start_i:end_i])
                doc_chunk = Chunk(
                    text=text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=split_id_counter,
                )
                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(doc):
                    break

                i += units - overlap  # Step forward, considering overlap

        return documents
