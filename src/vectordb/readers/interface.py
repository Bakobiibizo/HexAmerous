from enum import Enum

from goldenverba.components.component import VerbaComponent
from goldenverba.components.reader.document import Document


class InputForm(Enum):
    UPLOAD = "UPLOAD"  # Input Form to upload text files directly
    INPUT = "INPUT"  # Simple Text Input in Frontend
    CHUNKER = "CHUNKER"  # Default Input for Chunkers
    TEXT = "TEXT"  # Default Input for Embedder


class Reader(VerbaComponent):
    """
    Interface for Verba Readers.
    """

    def __init__(self):
        super().__init__()
        self.file_types = []
        self.input_form = InputForm.UPLOAD.value

    def load(
        bites: List[str],
        contents: List[str],
        paths: List[str],
        file_names: List[str],
        document_type: str,
    ) -> List[Document]:
        """Ingest data into Weaviate
        @parameter: bites : List[str] - List of bites
        @parameter: contents : List[str] - List of string content
        @parameter: paths : List[str] - List of paths to files
        @parameter: file_names : List[str] - List of file names
        @parameter: document_type : str - Document type
        @returns List[Document] - Lists of documents.
        """
        raise NotImplementedError("load method must be implemented by a subclass.")