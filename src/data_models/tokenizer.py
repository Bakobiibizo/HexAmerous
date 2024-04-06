from pydantic import BaseModel
from typing import Any, List, Dict, Optional, Union


class TokenizerConfig(BaseModel):
    name: str
    description: str 
    model: str
    tokenizer: str
    device: Any
    model_path: str