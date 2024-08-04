"""
Schema Generator. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
import re
import os
from dotenv import load_dotenv
from weaviate import Client
from loguru import logger
from typing_extensions import List, Dict, Optional, Tuple

load_dotenv()

VECTORIZERS = {"text2vec-openai", "text2vec-cohere"}  # Needs to match with Weaviate modules
EMBEDDINGS = {"MiniLM"}  # Custom Vectors

def strip_non_letters(s: str):
    """
    Replaces all non-alphanumeric characters in a string with underscores.

    Parameters:
        s (str): The input string.

    Returns:
        str: The modified string with non-alphanumeric characters replaced by underscores.
    """
    return re.sub(r"[^a-zA-Z0-9]", "_", s)

def verify_vectorizer(
    schema: Dict,
    vectorizer: str,
    skip_properties: Optional[List[str]] = None
) -> Dict:
    """
    Verify the vectorizer and update the schema accordingly.

    Args:
        schema (Dict): The schema to be modified.
        vectorizer (str): The name of the vectorizer.
        skip_properties (Optional[List[str]], optional): The list of properties to skip. Defaults to None.

    Returns:
        Dict: The modified schema.

    Raises:
        ValueError: If the `AZURE_OPENAI_RESOURCE_NAME` and `AZURE_OPENAI_EMBEDDING_MODEL` environment variables are not set when using the Azure OpenAI vectorizer.

    Description:
        This function verifies the vectorizer and updates the schema accordingly. It checks if the vectorizer is in the list of supported vectorizers (`VECTORIZERS`) and updates the schema accordingly. If the vectorizer is not in the list, it checks if it is in the list of supported embeddings (`EMBEDDINGS`). If the vectorizer is not None, it logs a warning message.

        If the vectorizer is the Azure OpenAI vectorizer and the `OPENAI_API_TYPE` environment variable is set to "azure", it checks if the `AZURE_OPENAI_RESOURCE_NAME` and `AZURE_OPENAI_EMBEDDING_MODEL` environment variables are set. If they are not set, it raises a `ValueError` with a specific error message.

        If the vectorizer is the Azure OpenAI vectorizer and the environment variables are set, it creates a `vectorizer_config` dictionary with the deployment ID and resource name. It then updates the schema by setting the vectorizer and module config.

        If any properties in the schema need to be skipped, it updates the module config for the vectorizer to skip the properties and set `vectorizePropertyName` to False.
    """
    if skip_properties is None:
        skip_properties = []
    modified_schema = schema.copy()

    #adding specific config for Azure OpenAI
    vectorizer_config = None
    if os.getenv("OPENAI_API_TYPE") == "azure" and vectorizer=="text2vec-openai":
        resource_name = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
        model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
        if resource_name is None or model is None:
            
            raise ValueError("AZURE_OPENAI_RESOURCE_NAME and AZURE_OPENAI_EMBEDDING_MODEL should be set when OPENAI_API_TYPE is azure. Resource name is XXX in http://XXX.openai.azure.com")
        vectorizer_config = { 
            "text2vec-openai": {
                    "deploymentId": model,
                    "resource_name": resource_name
            }
        }

    # Verify Vectorizer
    if vectorizer in VECTORIZERS:
        modified_schema["classes"][0]["vectorizer"] = vectorizer
        if vectorizer_config is not None:
            modified_schema["classes"][0]["module_config"] = vectorizer_config
        for prop in modified_schema["classes"][0]["properties"]:
            if prop["name"] in skip_properties:
                module_config = {
                    vectorizer: {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                }
                prop["module_config"] = module_config
    elif vectorizer in EMBEDDINGS:
        pass
    elif vectorizer is not None:
        logger.warning(f"Could not find matching vectorizer: {vectorizer}")

    return modified_schema

def add_suffix(
    schema: Dict, 
    vectorizer: str
    ) -> Tuple[Dict, str]:
    """
    A function that adds a suffix to the class property of the schema based on the vectorizer provided.

    Args:
        schema (Dict): The schema to be modified.
        vectorizer (str): The name of the vectorizer.

    Returns:
        Tuple[Dict, str]: A tuple containing the modified schema and the updated class property.
    """
    modified_schema = schema.copy()
    # Verify Vectorizer and add suffix
    modified_schema["classes"][0]["class"] = (
        modified_schema["classes"][0]["class"] + "_" + strip_non_letters(vectorizer)
    )
    return modified_schema, modified_schema["classes"][0]["class"]

def reset_schemas(
    client: Optional[Client] = None,
    vectorizer: Optional[str] = None,
):
    """
    Reset the schemas for a given client and vectorizer.

    Args:
        client (Optional[Client]): The client object used to interact with the schemas. Defaults to None.
        vectorizer (Optional[str]): The name of the vectorizer. Defaults to None.

    Returns:
        None
    """
    if not client or not vectorizer:
        return
    doc_name = f"Document_{strip_non_letters(vectorizer)}"
    chunk_name = f"Chunk_{strip_non_letters(vectorizer)}"
    cache_name = f"Cache_{strip_non_letters(vectorizer)}"

    client.schema.delete_class(doc_name)
    client.schema.delete_class(chunk_name)
    client.schema.delete_class(cache_name)

def init_schemas(
    client: Optional[Client]=None,
    vectorizer: Optional[str]=None,
    force: bool = False,
    check: bool = False,
) -> bool:
    """
    Initializes the schemas for a given client and vectorizer.

    Args:
        client (Optional[Client]): The client object used to interact with the schemas. Defaults to None.
        vectorizer (Optional[str]): The name of the vectorizer. Defaults to None.
        force (bool, optional): Whether to force the initialization even if the schemas already exist. Defaults to False.
        check (bool, optional): Whether to check if the schemas already exist before initializing. Defaults to False.

    Returns:
        bool: True if the schemas are successfully initialized, False otherwise.

    Raises:
        ValueError: If the schema initialization fails.

    """
    if not client or vectorizer:
        return False
    try:
        init_documents(client, vectorizer, force, check)
        init_cache(client, vectorizer, force, check)
        init_suggestion(client, force, check)
        return True
    except ValueError as e:
        logger.warning(f"Schema initialization failed {str(e)}")
        return False

def init_documents(
    client: Client, 
    vectorizer: Optional[str] = None, 
    force: bool = False, 
    check: bool = False
) -> Tuple[Dict, Dict]:
    """
    Initializes the schemas for a given client and vectorizer.

    Args:
        client (Client): The client object used to interact with the schemas.
        vectorizer (Optional[str], optional): The name of the vectorizer. Defaults to None.
        force (bool, optional): Whether to force the initialization even if the schemas already exist. Defaults to False.
        check (bool, optional): Whether to check if the schemas already exist before initializing. Defaults to False.

    Returns:
        Tuple[Dict, Dict]: A tuple containing the document schema and the chunk schema.

    Raises:
        ValueError: If the schema initialization fails.

    This function initializes the schemas for a given client and vectorizer. It creates two schema classes: "Document" and "Chunk". The "Document" class has properties such as "text", "doc_name", "doc_type", "doc_link", "timestamp", and "chunk_count". The "Chunk" class has properties such as "text", "doc_name", and "chunk_id". The function verifies the vectorizer and adds a suffix to the schema names. If the schema classes already exist, the function prompts the user to delete them. If the user agrees, the function deletes the schemas and creates new ones. Finally, the function returns the document schema and chunk schema.
    """
    if not vectorizer:
        return {}, {}
    SCHEMA_CHUNK = {
        "classes": [
            {
                "class": "Chunk",
                "description": "Chunks of Documentations",
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        # Skip
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        # Skip
                        "name": "doc_uuid",
                        "dataType": ["text"],
                        "description": "Document UUID",
                    },
                    {
                        # Skip
                        "name": "chunk_id",
                        "dataType": ["number"],
                        "description": "Document chunk from the whole document",
                    },
                ],
            }
        ]
    }
    SCHEMA_DOCUMENT = {
        "classes": [
            {
                "class": "Document",
                "description": "Documentation",
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        "name": "doc_link",
                        "dataType": ["text"],
                        "description": "Link to document",
                    },
                    {
                        "name": "timestamp",
                        "dataType": ["text"],
                        "description": "Timestamp of document",
                    },
                    {
                        "name": "chunk_count",
                        "dataType": ["number"],
                        "description": "Number of chunks",
                    },
                ],
            }
        ]
    }
    # Verify Vectorizer
    chunk_schema = verify_vectorizer(
        SCHEMA_CHUNK,
        vectorizer,
        ["doc_type", "doc_uuid", "chunk_id"],
    )

    # Add Suffix
    document_schema, document_name = add_suffix(SCHEMA_DOCUMENT, vectorizer)
    chunk_schema, chunk_name = add_suffix(chunk_schema, vectorizer)

    if client.schema.exists(document_name):
        if check:
            return document_schema, chunk_schema
        if not force:
            user_input = input(
                f"{document_name} class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.schema.delete_class(document_name)
            client.schema.delete_class(chunk_name)
            client.schema.create(document_schema)
            client.schema.create(chunk_schema)
            logger.info(f"{document_name} and {chunk_name} schemas created")
        else:
            logger.warning(
                f"Skipped deleting {document_name} and {chunk_name} schema, nothing changed"
            )
    else:
        client.schema.create(document_schema)
        client.schema.create(chunk_schema)
        logger.info(f"{document_name} and {chunk_name} schemas created")

    return document_schema, chunk_schema

def init_cache(
    client: Client, 
    vectorizer: Optional[str] = None, 
    force: bool = False, 
    check: bool = False
) -> Dict:
    """
    Initializes the cache schema for a given client and vectorizer.

    Args:
        client (Client): The client object used to interact with the schemas.
        vectorizer (Optional[str]): The name of the vectorizer. Defaults to None.
        force (bool, optional): Whether to force the initialization even if the schemas already exist. Defaults to False.
        check (bool, optional): Whether to check if the schemas already exist before initializing. Defaults to False.

    Returns:
        Dict: The cache schema.
    """
    if not vectorizer:
        return {}
    SCHEMA_CACHE = {
        "classes": [
            {
                "class": "Cache",
                "description": "Cache of Documentations and their queries",
                "properties": [
                    {
                        "name": "query",
                        "dataType": ["text"],
                        "description": "Query",
                    },
                    {
                        # Skip
                        "name": "system",
                        "dataType": ["text"],
                        "description": "System message",
                    },
                ],
            }
        ]
    }

    # Verify Vectorizer
    cache_schema = verify_vectorizer(
        SCHEMA_CACHE,
        vectorizer,
        ["system", "results"],
    )

    # Add Suffix
    cache_schema, cache_name = add_suffix(cache_schema, vectorizer)

    if client.schema.exists(cache_name):
        if check:
            return cache_schema
        if not force:
            user_input = input(
                f"{cache_name} class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.schema.delete_class(cache_name)
            client.schema.create(cache_schema)
            logger.info(f"{cache_name} schema created")
        else:
            logger.warning(f"Skipped deleting {cache_name} schema, nothing changed")
    else:
        client.schema.create(cache_schema)
        logger.info(f"{cache_name} schema created")

    return cache_schema

def init_suggestion(
    client: Client,
    force: bool = False,
    check: bool = False
) -> Dict:
    """
    Initializes the schema for suggestions based on the client, force flag, and check flag.

    Args:
        client (Client): The client object used to interact with the schemas.
        force (bool, optional): Whether to force the initialization even if the schema exists. Defaults to False.
        check (bool, optional): Whether to check if the schema already exists before initializing. Defaults to False.

    Returns:
        Dict: The schema for suggestions.

    """
    SCHEMA_SUGGESTION = {
        "classes": [
            {
                "class": "Suggestion",
                "description": "List of possible prompts",
                "properties": [
                    {
                        "name": "suggestion",
                        "dataType": ["text"],
                        "description": "Query",
                    },
                ],
            }
        ]
    }

    suggestion_schema = SCHEMA_SUGGESTION
    suggestion_name = "Suggestion"

    if client.schema.exists(suggestion_name):
        if check:
            return suggestion_schema
        if not force:
            user_input = input(
                f"{suggestion_name} class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.schema.delete_class(suggestion_name)
            client.schema.create(suggestion_schema)
            logger.info(f"{suggestion_name} schema created")
        else:
            logger.warning(f"Skipped deleting {suggestion_name} schema, nothing changed")
    else:
        client.schema.create(suggestion_schema)
        logger.info(f"{suggestion_name} schema created")

    return suggestion_schema