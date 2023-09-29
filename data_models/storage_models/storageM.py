from pydantic import BaseModel, validator
from typing import Any, Dict



class StorageModel(BaseModel):
    name: StorageEnum
    model: Any

    @validator('model', pre=True, always=True)
    def validate_model(cls, value: Any, values: Dict[str, Any]) -> Any:
        """
        Validation of the model ensuring its of the StorageEnum type
        """
        if name := values.get('name'):
            expected_type = name.value
            if not isinstance(value, expected_type):
                raise ValueError(f"Model must be an instance of {expected_type}")
        return value