
from abc import ABC, abstractmethod
from typing import Any, List, Dict

class RetrieverABC(ABC):
    """
    Abstract base class for Retriever.
    Defines the contract that any specific Retriever must follow.
    """

    @abstractmethod
    def search(self, query: Any, options: Dict = None) -> List[Any]:
        """
        Search the vector store based on the query and return results.
        """
        pass

    @abstractmethod
    def max_marginal_relevance_search(self, query: Any, options: Dict = None) -> List[Any]:
        """
        Perform a Max Marginal Relevance search based on the query.
        """
        pass

    @abstractmethod
    def similarity_search(self, query: Any, options: Dict = None) -> List[Any]:
        """
        Perform a similarity search based on the query.
        """
        pass

    @abstractmethod
    def similarity_search_by_vector(self, vector: Any, options: Dict = None) -> List[Any]:
        """
        Perform a similarity search based on the provided vector.
        """
        pass
