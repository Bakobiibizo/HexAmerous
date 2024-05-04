from pydantic import BaseModel, Field
from typing import Union, List, Dict
from datetime import date as Date
from uuid import uuid4
from src.data_models.component import Component

class Chunk(BaseModel):
    text: str = Field(default="")
    text_no_overlap: str = Field(default="")
    doc_name: str = Field(default="")
    doc_type: str = Field(default="")
    doc_uuid: str = Field(default="")
    chunk_id: str = Field(default="")

    def __setattr__(self, name, value):
       if name in self.__dict__:
           field = self.__fields__.get(name)
           if field:
               value = field.(value)
           super().__setattr__(name, value)
       else:
           raise AttributeError(f"Document has no attribute {name}")
       
    class Config:
        # If you need to handle arbitrary data types or custom validation
        # you can add configurations here
        pass

class Chunker(Component):
    """
    Interface for Verba Chunking.
    """

    def __init__(self):
        super().__init__()
        self.input_form = InputForm.CHUNKER.value  # Default for all Chunkers
        self.default_units = 100
        self.default_overlap = 50

    def chunk(
        self, documents: list[Document], units: int, overlap: int
    ) -> list[Document]:
        """Chunk verba documents into chunks based on units and overlap.

        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks.
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")
