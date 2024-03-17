from pydantic import BaseModel, Field
from typing import Union, List, Dict
from datetime import date as Date
from uuid import uuid4

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
               value = field.type_(value)
           super().__setattr__(name, value)
       else:
           raise AttributeError(f"Document has no attribute {name}")
       
    class Config:
        # If you need to handle arbitrary data types or custom validation
        # you can add configurations here
        pass