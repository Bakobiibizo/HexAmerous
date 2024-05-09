from typing_extensions import List
from src.vectordb.readers.document import Document
from src.vectordb.readers.interface import InputForm
from src.vectordb.component import Component


class Chunker(Component):
    """
    Interface for Verba Chunking.
    """

    def __init__(self, name, description, requires_library, requires_env):
        """
        Initializes the Chunker object.

        This method initializes the Chunker object by calling the __init__ method of the parent class using the super() function. It sets the `input_form` attribute to the value of `InputForm.CHUNKER.value`, which represents the default input form for all chunkers. It also sets the `default_units` attribute to 100 and the `default_overlap` attribute to 50.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__(
            name=name,
            requires_env=requires_env,
            requires_library=requires_library,
            description=description,
        )
        self.input_form = InputForm.CHUNKER.value  # Default for all Chunkers
        self.default_units = 100
        self.default_overlap = 50

    def chunk(
        self, documents: List[Document], units: int, overlap: int
    ) -> List[Document]:
        """
        Chunk verba documents into chunks based on units and overlap.

        This method takes a List of Verba documents, the number of units per chunk, and the overlap between chunks. It raises a NotImplementedError because the chunk method must be implemented by a subclass.

        Parameters:
            documents (List[Document]): A List of Verba documents to be chunked.
            units (int): The number of units per chunk (words, sentences, etc.).
            overlap (int): The amount of overlap between chunks.

        Returns:
            List[Document]: A List of chunked documents.

        Raises:
            NotImplementedError: If the chunk method is not implemented by a subclass.
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")
