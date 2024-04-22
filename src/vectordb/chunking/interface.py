from pydantic import BaseModel

from interface import InputForm
from vectordb import

class Chunker(Component):
    """
    Interface for Verba Chunking.
    """

    def __init__(self):
        """
        Initializes the Chunker object.

        This method initializes the Chunker object by calling the __init__ method of the parent class using the super() function. It sets the `input_form` attribute to the value of `InputForm.CHUNKER.value`, which represents the default input form for all chunkers. It also sets the `default_units` attribute to 100 and the `default_overlap` attribute to 50.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.input_form = InputForm.CHUNKER.value  # Default for all Chunkers
        self.default_units = 100
        self.default_overlap = 50

    def chunk(
        self, documents: List[Document], units: int, overlap: int
    ) -> List[Document]:
        """Chunk verba documents into chunks based on units and overlap.

        @parameter: documents : List[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns List[str] - List of documents that contain the chunks.
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")

