import weaviate
from typing import List, Dict
import os

client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
)

def store_document(document: Dict[str, str]) -> str:
    """
    Store a document in Weaviate.
    
    Args:
    document (Dict[str, str]): A dictionary containing the document data.
    
    Returns:
    str: The UUID of the stored document.
    """
    return client.data_object.create(
        data_object=document,
        class_name="Document"
    )

def retrieve_documents(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    Retrieve documents from Weaviate based on a semantic search query.
    
    Args:
    query (str): The search query.
    limit (int): The maximum number of documents to retrieve.
    
    Returns:
    List[Dict[str, str]]: A list of retrieved documents.
    """
    result = (
        client.query
        .get("Document", ["content", "metadata"])
        .with_near_text({"concepts": [query]})
        .with_limit(limit)
        .do()
    )
    return result["data"]["Get"]["Document"]

def retrieve_file_chunks(file_ids: List[str], query: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    Retrieve file chunks from Weaviate based on file IDs and a semantic search query.
    
    Args:
    file_ids (List[str]): List of file IDs to search within.
    query (str): The search query.
    limit (int): The maximum number of chunks to retrieve.
    
    Returns:
    List[Dict[str, str]]: A list of retrieved file chunks.
    """
    result = (
        client.query
        .get("FileChunk", ["content", "metadata"])
        .with_near_text({"concepts": [query]})
        .with_where({
            "path": ["metadata", "file_id"],
            "operator": "In",
            "valueString": file_ids
        })
        .with_limit(limit)
        .do()
    )
    return result["data"]["Get"]["FileChunk"]