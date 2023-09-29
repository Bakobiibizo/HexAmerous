from pydantic import BaseModel
from typing import List, Optional

class Tool(BaseModel):
    """
    Model for managing tools
    """
    name: str
    description: str
    command: str
    api: str

class Tools(BaseModel):
    """
    Model for managing tools
    """
    name: str
    tools: List[Tool]
    notes: Optional[str]
    
    