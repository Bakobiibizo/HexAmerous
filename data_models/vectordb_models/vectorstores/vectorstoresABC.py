from abc import ABC, abstractmethod
from typing import Any, List, Dict

class AbstractVectorStore(ABC):
    """
    Abstract base class for VectorStore.
    Defines the contract that any specific VectorStore must follow.
    """

    @abstractmethod
    def add_document(self, document: Any) -> None:
        """
        Add a document to the vector store.
        """
        pass

    @abstractmethod
    def get_collection(self) -> Any:
        """
        Retrieve the entire collection from the vector store.
        """
        pass

    @abstractmethod
    def get_vectorstore(self) -> Any:
        """
        Retrieve the stored vector store itself.
        """
        pass

    @abstractmethod
    def register_vectorstore(self, config: Dict) -> None:
        """
        Register a new vector store based on configuration.
        """
        pass

    @abstractmethod
    def remove_vectorstore(self) -> None:
        """
        Remove the currently active vector store.
        """
        pass

    @abstractmethod
    def manage_vectorstore(self, action: str, params: Dict) -> Any:
        """
        General manager function for handling various vector store actions.
        """
        pass
