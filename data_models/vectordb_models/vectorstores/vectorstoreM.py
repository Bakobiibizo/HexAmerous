from pydantic import BaseModel
from typing import Dict, Union

class DocumentModel(BaseModel):
    text: str
    metadata: Dict[str, Union[str, int, float]]

class QueryModel(BaseModel):
    text: str
    parameters: Dict[str, Union[str, int, float]]

class VectorStoreConfigModel(BaseModel):
    type: str
    url: str
    credentials: Dict[str, str]
    other_settings: Dict[str, Union[str, int, float]]

class SearchOptionsModel(BaseModel):
    limit: int
    sort: str
    filters: Dict[str, Union[str, int, float]]

class ActionResultModel(BaseModel):
    status: str
    data: Union[Dict, None]
    error: Union[str, None]
