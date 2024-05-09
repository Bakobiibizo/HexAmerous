from typing_extensions import List
from pydantic import BaseModel


class Component(BaseModel):
    name: str
    requires_env: List[str]
    requires_library: List[str]
    description: str
