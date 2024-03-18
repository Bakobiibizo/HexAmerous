from pydantic import BaseModel, Field
from typing import Union, List, Dict
from datetime import date as Date

class Document(BaseModel):
    text: str = Field(default="")
    type: str = Field(default="")
    name: str = Field(default="")
    path: str = Field(default="")
    link: str = Field(default="")
    timestamp: Date = Field(default=Date.today().ctime().format("%Y-%m-%d %H:%M:%S"))
    reader: str
    meta: Dict = Field(default={})
    doc_uuid: str = Field(default="")
    chunk_id: str = Field(default="")
    tokens: int = Field(default=0)
    vector: Union[List[float], None] = Field(default=None)
    score: float = Field(default=0.0)

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