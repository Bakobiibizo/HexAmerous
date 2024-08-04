"""
Reader Interface. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
from enum import Enum
from typing_extensions import List

from src.vectordb.component import Component
from src.vectordb.readers.document import Document


class InputForm(Enum):
    UPLOAD = "UPLOAD"  # Input Form to upload text files directly
    INPUT = "INPUT"  # Simple Text Input in Frontend
    CHUNKER = "CHUNKER"  # Default Input for Chunkers
    TEXT = "TEXT"  # Default Input for Embedder


class Reader(Component):
    """
    Interface for Verba Readers.
    """
    def __init__(
        self,
        name,
        description,
        requires_library,
        requires_env,
        ):
        """
        Initializes a new instance of the class.

        Args:
            name (str): The name of the instance.
            description (str): The description of the instance.
            requires_library (List[str]): A list of libraries required by the instance.
            requires_env (List[str]): A list of environment variables required by the instance.

        Returns:
            None
        """
        super().__init__(
            name=name,
            description=description,
            requires_library=requires_library,
            requires_env=requires_env,
        )
        self.file_types = []
        self.input_form = InputForm.UPLOAD.value

    def load(
        self,
        bites: List[str],
        contents: List[str],
        paths: List[str],
        file_names: List[str],
        document_type: str,
    ) -> List[Document]:
        """
        Load the data from the given sources and return a list of Document objects.

        Args:
            bites (List[str]): A list of base64-encoded strings representing data.
            contents (List[str]): A list of strings containing document contents.
            paths (List[str]): A list of file paths to load data from.
            file_names (List[str]): A list of file names corresponding to the paths.
            document_type (str): The type of document to load.

        Returns:
            List[Document]: A list of Document objects loaded from the data sources.

        Raises:
            NotImplementedError: If the load method is not implemented by a subclass.
        """
        raise NotImplementedError("load method must be implemented by a subclass.")