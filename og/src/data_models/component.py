from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any


class Component(BaseModel):
    name: str
    required_env: List[str] 
    required_library: List[str] 
    description: str

        