from abc import ABC, abstractmethod
from typing import Any, List, Dict
from data_models.storage_models.storageM import StorageModel

class StorageABC(ABC):
    """
    Database manager for sql style data base.
    """

    def __init__(self, db_connection: Any) -> None:
        """
        Initialize the class
        """
        self.db_connection = db_connection

    @abstractmethod
    def create_table(self) -> None:
        """
        Create a table in the database
        """

    @abstractmethod
    def insert_model(self, name: str, storage_model: StorageModel) -> None:
        """
        Insert a new model
        """

    @abstractmethod
    def get_all_models(self) -> List[Dict[str, str]]:
        """
        Fetch all models
        """

    @abstractmethod
    def update_model(self, name: str, storage_model: StorageModel) -> None:
        """
        Update the database entry for a model
        """

    @abstractmethod
    def delete_model(self, name: str) -> None:
        """
        Delete a model from the database
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection
        """
