"""
Embedder Interface. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""

from tqdm import tqdm
from typing import List, Dict, Tuple, Union, Optional
from weaviate import Client
from loguru import logger
from src.vectordb.readers.document import Document
from src.vectordb.readers.interface import InputForm
from src.vectordb.component import Component
from src.vectordb.schema.schema_generator import (
    VECTORIZERS,
    EMBEDDINGS,
    strip_non_letters,
)


class Embedder(Component):
    """
    Interface for Verba Embedding.
    """

    def __init__(
        self,
        name: str,
        description: str,
        requires_env: List[str],
        requires_library: Optional[List[str]] = None,
    ):
        """
        Initializes a new instance of the class.

        Args:
            name (str): The name of the instance.
            description (str): The description of the instance.
            requires_env (List[str]): A list of environment variables required by the instance.
            requires_library (List[str]): A list of libraries required by the instance.

        Returns:
            None
        """
        super().__init__(
            name=name,
            description=description,
            requires_env=requires_env,
            requires_library=requires_library,
        )
        self.input_form = InputForm.TEXT.value  # Default for all Embedders
        self.vectorizer = ""

    def embed(
        self, documents: List[Document], client: Client, batch_size: int = 100
    ) -> bool:
        """
        A method for embedding data using the given client and batch size.

        Args:
            self: The object instance.
            client (Client): The Weaviate client used to interact with the Weaviate server.
            batch_size (int): The size of the batch for embedding data. Default is 100.

        Returns:
            bool: Indicates whether the embedding was successful.

        Raises:
            NotImplementedError: If the embed method is not implemented by a subclass.
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")

    def import_data(
        self,
        documents: List[Document],
        client: Client,
    ) -> bool:
        """
        Imports data into the Weaviate client.

        Args:
            self (Embedder): The Embedder instance.
            documents (List[Document]): The list of Document objects to import.
            client (Client): The Weaviate client.

        Returns:
            bool: True if the data is successfully imported, False otherwise.

        Raises:
            ValueError: If an exception occurs during the data import process.
        """
        try:
            if self.vectorizer not in VECTORIZERS and self.vectorizer not in EMBEDDINGS:
                logger.warning(f"Vectorizer of {self.name} not found")
                return False

            for i, document in enumerate(documents):
                batches = []
                uuid = ""
                temp_batch = []
                token_counter = 0
                for chunk in document.chunks:
                    if not chunk or not chunk.tokens:
                        break
                    if token_counter + chunk.tokens <= 5000:
                        token_counter += chunk.tokens
                        temp_batch.append(chunk)
                    else:
                        batches.append(temp_batch.copy())
                        token_counter = chunk.tokens
                        temp_batch = [chunk]
                if len(temp_batch) > 0:
                    batches.append(temp_batch.copy())
                    token_counter = 0
                    temp_batch = []

                logger.info(
                    f"({i+1}/{len(documents)}) Importing document {document.name} with {len(batches)} batches"
                )

                with client.batch as batch:
                    batch.batch_size = 1
                    properties = {
                        "text": str(document.text),
                        "doc_name": str(document.name),
                        "doc_type": str(document.type),
                        "doc_link": str(document.link),
                        "chunk_count": len(document.chunks),
                        "timestamp": str(document.timestamp),
                    }

                    class_name = f"Document_{strip_non_letters(self.vectorizer)}"
                    uuid = client.batch.add_data_object(properties, class_name)

                    for chunk in document.chunks:
                        chunk.set_uuid(uuid)

                chunk_count = 0
                for _batch_id, chunk_batch in tqdm(
                    enumerate(batches), total=len(batches), desc="Importing batches"
                ):
                    with client.batch as batch:
                        batch.batch_size = len(chunk_batch)
                        for chunk in chunk_batch:
                            chunk_count += 1

                            properties = {
                                "text": chunk.text,
                                "doc_name": str(document.name),
                                "doc_uuid": chunk.doc_uuid,
                                "doc_type": chunk.doc_type,
                                "chunk_id": chunk.chunk_id,
                            }
                            class_name = f"Chunk_{strip_non_letters(self.vectorizer)}"

                            # Check if vector already exists
                            if chunk.vector is None:
                                client.batch.add_data_object(properties, class_name)
                            else:
                                client.batch.add_data_object(
                                    properties, class_name, vector=chunk.vector
                                )
                if not document.name:
                    document.__setattr__(name="name", value="uuid", obj=document)
                self.check_document_status(
                    client,
                    uuid,
                    str(document.name),
                    f"Document_{strip_non_letters(self.vectorizer)}",
                    f"Chunk_{strip_non_letters(self.vectorizer)}",
                    len(document.chunks),
                )
            return True
        except Exception as e:
            raise ValueError(e) from e

    def check_document_status(
        self,
        client: Client,
        doc_uuid: str,
        doc_name: str,
        doc_class_name: str,
        chunk_class_name: str,
        chunk_count: int,
    ):
        """
        Verifies that imported documents and its chunks exist in the database, if not, remove everything that was added and rollback.

        :param client: Client - Weaviate Client
        :param doc_uuid: str - Document UUID
        :param doc_name: str - Document name
        :param doc_class_name: str - Class name of Document
        :param chunk_class_name: str - Class name of Chunks
        :param chunk_count: int - Number of expected chunks
        :raises ValueError: If the document is not found or the chunk mismatch occurs
        :return: None
        """
        document = client.data_object.get_by_id(
            doc_uuid,
            class_name=doc_class_name,
        )

        if document is None:
            raise ValueError(f"Document {doc_uuid} not found {document}")
        results = (
            client.query.get(
                class_name=chunk_class_name,
                properties=[
                    "doc_name",
                ],
            )
            .with_where(
                {
                    "path": ["doc_uuid"],
                    "operator": "Equal",
                    "valueText": doc_uuid,
                }
            )
            .with_limit(chunk_count + 1)
            .do()
        )

        if len(results["data"]["Get"][chunk_class_name]) != chunk_count:
            # Rollback if fails
            self.remove_document(client, doc_name, doc_class_name, chunk_class_name)
            raise ValueError(
                f"Chunk mismatch for {doc_uuid} {len(results['data']['Get'][chunk_class_name])} != {chunk_count}"
            )

    def remove_document(
        self, client: Client, doc_name: str, doc_class_name: str, chunk_class_name: str
    ) -> None:
        """
        Removes a document and its chunks from the database.

        Args:
            client (Client): The Weaviate client used to interact with the database.
            doc_name (str): The name of the document to be removed.
            doc_class_name (str): The class name of the document.
            chunk_class_name (str): The class name of the chunks.

        Returns:
            None
        """
        client.batch.delete_objects(
            class_name=doc_class_name,
            where={"path": ["doc_name"], "operator": "Equal", "valueText": doc_name},
        )

        client.batch.delete_objects(
            class_name=chunk_class_name,
            where={"path": ["doc_name"], "operator": "Equal", "valueText": doc_name},
        )

        logger.warning(f"Deleted document {doc_name} and its chunks")

    def remove_document_by_id(self, client: Client, doc_id: str):
        """
        Removes a document and its chunks from the database by their document ID.

        Args:
            client (Client): The Weaviate client used to interact with the database.
            doc_id (str): The ID of the document to be removed.

        Returns:
            None
        """
        doc_class_name = f"Document_{strip_non_letters(self.vectorizer)}"
        chunk_class_name = f"Chunk_{strip_non_letters(self.vectorizer)}"

        client.data_object.delete(uuid=doc_id, class_name=doc_class_name)

        client.batch.delete_objects(
            class_name=chunk_class_name,
            where={"path": ["doc_uuid"], "operator": "Equal", "valueText": doc_id},
        )

        logger.warning(f"Deleted document {doc_id} and its chunks")

    def get_document_class(self) -> str:
        """
        Returns the document class name based on the vectorizer.

        :return: A string representing the document class name.
        :rtype: str
        """
        return f"Document_{strip_non_letters(self.vectorizer)}"

    def get_chunk_class(self) -> str:
        """
        Returns the chunk class name based on the vectorizer.

        :return: A string representing the chunk class name.
        :rtype: str
        """
        return f"Chunk_{strip_non_letters(self.vectorizer)}"

    def get_cache_class(self) -> str:
        """
        Returns the cache class name based on the vectorizer.

        :return: A string representing the cache class name.
        :rtype: str
        """
        return f"Cache_{strip_non_letters(self.vectorizer)}"

    def search_documents(self, client: Client, query: str, doc_type: str) -> List:
        """
        Search for documents from Weaviate based on the given query and document type.

        Args:
            client (Client): The Weaviate client used to query the database.
            query (str): The search query.
            doc_type (str): The document type to search for. If None, all document types will be searched.

        Returns:
            List: A list of documents matching the search query.
        """
        doc_class_name = f"Document_{strip_non_letters(self.vectorizer)}"

        if not doc_type or doc_type is None:
            query_results = (
                client.query.get(
                    class_name=doc_class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_bm25(query, properties=["doc_name"])
                .with_additional(properties=["id"])
                .with_limit(100)
                .do()
            )
        else:
            query_results = (
                client.query.get(
                    class_name=doc_class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_bm25(query, properties=["doc_name"])
                .with_where(
                    {
                        "path": ["doc_type"],
                        "operator": "Equal",
                        "valueText": doc_type,
                    }
                )
                .with_additional(properties=["id"])
                .with_limit(100)
                .do()
            )

        return query_results["data"]["Get"][doc_class_name]

    def get_need_vectorization(self) -> bool:
        """
        Check if the current vectorizer is in the list of embeddings.

        Returns:
            bool: True if the vectorizer is in the list of embeddings, False otherwise.
        """
        return self.vectorizer in EMBEDDINGS

    def vectorize_query(self, query: str):
        """
        Vectorizes a query by calling the vectorize_chunk method and returns the resulting vector.

        :param query: The query to be vectorized.
        :type query: str
        :return: A list of floats representing the vectorized query.
        :rtype: List[float]
        :raises NotImplementedError: If the vectorize_query method is not implemented by a subclass.
        """
        raise NotImplementedError(
            "vectorize_query method must be implemented by a subclass."
        )

    def conversation_to_query(self, queries: List[str], conversation: Dict) -> str:
        """
        Converts a conversation to a query string by extracting relevant information from the conversation and joining it with the provided queries.

        Parameters:
            queries (List[str]): A list of queries.
            conversation (Dict): A dictionary representing a conversation, where each key-value pair represents a message in the conversation.

        Returns:
            str: The resulting query string.

        Example:
            >>> queries = ["What is the weather like?", "How cold is it?"]
            >>> conversation = {
            ...     0: {"type": "user", "content": "What is the weather like today?"},
            ...     1: {"type": "system", "content": "The weather is cold and rainy."},
            ...     2: {"type": "user", "content": "How cold is it?"}
            ... }
            >>> conversation_to_query(queries, conversation)
            'the weather like today ? how cold is it ?'
        """
        query = ""

        if len(conversation) > 1:
            if conversation[-1].type == "system":
                query += f"{conversation[-1].content} "
            elif conversation[-2].type == "system":
                query += f"{conversation[-2].content} "

        for _query in queries:
            query += f"{_query} "

        return query.lower()

    def retrieve_semantic_cache(
        self, client: Client, query: str, dist: float = 0.04
    ) -> Union[str, Tuple[Union[str, None], Union[float, None]]]:
        """
        Retrieve results from semantic cache based on query and distance threshold.

        :param client: The client object used to query the semantic cache.
        :type client: Client
        :param query: The query string to search for in the semantic cache.
        :type query: str
        :param dist: The distance threshold for the semantic cache search. Defaults to 0.04.
        :type dist: float
        :return: A tuple containing the system response and the distance between the query and the cached query, if found. Otherwise, returns (None, None).
        :rtype: Union[Tuple[str, float], Tuple[None, None]]
        """
        needs_vectorization = self.get_need_vectorization()

        match_results = (
            client.query.get(
                class_name=self.get_cache_class(),
                properties=["query", "system"],
            )
            .with_where(
                {
                    "path": ["query"],
                    "operator": "Equal",
                    "valueText": query,
                }
            )
            .with_limit(1)
        ).do()
        if not match_results["data"]:
            return None, None
        if (
            "data" in match_results
            and len(match_results["data"]["Get"][self.get_cache_class()]) > 0
            and (
                query
                == match_results["data"]["Get"][self.get_cache_class()][0]["query"]
            )
        ):
            logger.info("Direct match from cache")
            if not match_results["data"]["Get"][self.get_cache_class()][0]["system"]:
                return None, None
            return (
                match_results["data"]["Get"][self.get_cache_class()][0]["system"],
                0.0,
            )

        query_results = (
            client.query.get(
                class_name=self.get_cache_class(),
                properties=["query", "system"],
            )
            .with_additional(properties=["distance"])
            .with_limit(1)
        )

        if needs_vectorization:
            vector = self.vectorize_query(query)
            query_results = query_results.with_near_vector(
                content={"vector": vector},
            ).do()

        else:
            query_results = query_results.with_near_text(
                content={"concepts": [query]},
            ).do()

        if "data" not in query_results:
            logger.warning(query_results)
            return None, None

        results = query_results["data"]["Get"][self.get_cache_class()]

        if not results:
            return None, None

        result = results[0]

        if float(result["_additional"]["distance"]) > dist:
            return None, None
        logger.info("Retrieved similar from cache")
        return result["system"], float(result["_additional"]["distance"])

    def add_to_semantic_cache(self, client: Client, query: str, system: str):
        """
        Adds a query and its corresponding system response to the semantic cache.

        Parameters:
            client (Client): The Weaviate client used to interact with the semantic cache.
            query (str): The query string to be added to the semantic cache.
            system (str): The system response corresponding to the query.

        Returns:
            None
        """
        needs_vectorization = self.get_need_vectorization()

        with client.batch as batch:
            batch.batch_size = 1
            properties = {"query": query, "system": system}
            logger.info("Saved to cache")

            if needs_vectorization:
                vector = self.vectorize_query(query)
                client.batch.add_data_object(
                    properties, self.get_cache_class(), vector=vector
                )
            else:
                client.batch.add_data_object(properties, self.get_cache_class())
