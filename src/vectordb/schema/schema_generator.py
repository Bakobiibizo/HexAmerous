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
    return re.sub(r"[^a-zA-Z0-9]", "_", s)

def verify_vectorizer(
    schema: Dict,
    vectorizer: str,
    skip_properties: Optional[List[str]] = None
) -> Dict:
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