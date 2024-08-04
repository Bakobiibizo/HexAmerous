"""
Window Retriever. Based one Weaviate's Verba.
https://github.com/weaviate/Verba
"""
from weaviate.client import Client
from weaviate.hybrid import HybridFusion
from typing import List, Tuple

from src.vectordb.embedders.interface import Embedder
from src.vectordb.chunkers.chunk import Chunk
from src.vectordb.retrievers.interface import Retriever


class WindowRetriever(Retriever):
    """
    Window Retriever. uses hybrid search to retrieve relevant chunks and adds their surrounding context
    """
    def __init__(self):
        """
        Initialize a new instance of the WindowRetriever class.

        This method initializes the attributes of the WindowRetriever class, including the description and name.
        It calls the __init__ method of the parent class to ensure proper initialization.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__(
            name="WindowRetriever",
            description="WindowRetriever uses Hybrid Search to retrieve relevant chunks and adds their surrounding context",
            requires_env=[],
            requires_library=[]            
        )
        self.description = "WindowRetriever uses Hybrid Search to retrieve relevant chunks and adds their surrounding context"
        self.name = "WindowRetriever"

    def retrieve(
        self,
        queries: List[str],
        client: Client,
        embedder: Embedder,
    ) -> Tuple[List[Chunk], str]:
        """
        Retrieve chunks from Weaviate based on the given queries and return them sorted and with their surrounding context.

        Parameters:
            queries (List[str]): A List of queries to search for chunks.
            client (Client): The Weaviate client used to query the database.
            embedder (Embedder): The embedder used to vectorize the queries.

        Returns:
            Tuple(List[Chunk], str): A Tuple containing a List of sorted chunks and the combined context string.
        """

        chunk_class = embedder.get_chunk_class()
        needs_vectorization = embedder.get_need_vectorization()
        chunks = []

        for query in queries:
            query_results = (
                client.query.get(
                    class_name=chunk_class,
                    properties=[
                        "text",
                        "doc_name",
                        "chunk_id",
                        "doc_uuid",
                        "doc_type",
                    ],
                )
                .with_additional(properties=["score"])
                .with_autocut(2)
            )

            if needs_vectorization:
                vector = embedder.vectorize_query(query)
                query_results = query_results.with_hybrid(
                    query=query,
                    vector=vector,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    properties=[
                        "text",
                    ],
                ).do()

            else:
                query_results = query_results.with_hybrid(
                    query=query,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    properties=[
                        "text",
                    ],
                ).do()

            for chunk in query_results["data"]["Get"][chunk_class]:
                chunk_obj = Chunk(
                    chunk["text"],
                    chunk["doc_name"],
                    chunk["doc_type"],
                    chunk["doc_uuid"],
                    chunk["chunk_id"],
                )
                chunk_obj.set_score(chunk["_additional"]["score"])
                chunks.append(chunk_obj)

        sorted_chunks = self.sort_chunks(chunks)

        context = self.combine_context(sorted_chunks, client, embedder)

        return sorted_chunks, context

    def combine_context(
        self,
        chunks: List[Chunk],
        client: Client,
        embedder: Embedder,
    ) -> str:
        """
        Combines the context of the given chunks by retrieving and adding surrounding chunks to the map.

        Args:
            chunks (List[Chunk]): A List of chunks to combine context for.
            client (Client): The Weaviate client used to query the database.
            embedder (Embedder): The embedder used to vectorize the queries.

        Returns:
            str: The combined context string of the chunks.

        Description:
            This function takes a List of chunks and combines their context by retrieving and adding surrounding chunks to a map.
            The function iterates over each chunk in the List and checks if its document name is already in the map. If not, it adds an empty Dictionary for that document name.
            Then, for each chunk, it retrieves the chunk ID and creates a range of chunk IDs around it. It iterates over this range and checks if the chunk ID is not already in the map and not in the added chunks Dictionary.
            If the conditions are met, it queries the Weaviate client for the chunk with the given chunk ID and document name. If the query returns a result, it creates a Chunk object from the result and adds it to the added chunks Dictionary.
            Finally, it combines the context of the added chunks and returns it as a string.
        """
        doc_name_map = {}

        context = ""

        for chunk in chunks:
            if chunk.doc_name not in doc_name_map:
                doc_name_map[chunk.doc_name] = {}

            doc_name_map[chunk.doc_name][chunk.chunk_id] = chunk

        window = 2
        for doc, chunk_map in doc_name_map.items():
            added_chunks = {}
            for chunk in chunk_map:
                chunk_id = int(chunk)
                all_chunk_range = list(range(chunk_id - window, chunk_id + window + 1))
                for _range in all_chunk_range:
                    if (
                        _range >= 0
                        and _range not in chunk_map
                        and _range not in added_chunks
                    ):
                        chunk_retrieval_results = (
                            client.query.get(
                                class_name=embedder.get_chunk_class(),
                                properties=[
                                    "text",
                                    "doc_name",
                                    "chunk_id",
                                    "doc_uuid",
                                    "doc_type",
                                ],
                            )
                            .with_where(
                                {
                                    "operator": "And",
                                    "operands": [
                                        {
                                            "path": ["chunk_id"],
                                            "operator": "Equal",
                                            "valueNumber": _range,
                                        },
                                        {
                                            "path": ["doc_name"],
                                            "operator": "Equal",
                                            "valueText": chunk_map[chunk].doc_name,
                                        },
                                    ],
                                }
                            )
                            .with_limit(1)
                            .do()
                        )

                        if "data" in chunk_retrieval_results and chunk_retrieval_results["data"]["Get"][
                                                        embedder.get_chunk_class()
                                                    ]:
                            chunk_obj = Chunk(
                                chunk_retrieval_results["data"]["Get"][
                                    embedder.get_chunk_class()
                                ][0]["text"],
                                chunk_retrieval_results["data"]["Get"][
                                    embedder.get_chunk_class()
                                ][0]["doc_name"],
                                chunk_retrieval_results["data"]["Get"][
                                    embedder.get_chunk_class()
                                ][0]["doc_type"],
                                chunk_retrieval_results["data"]["Get"][
                                    embedder.get_chunk_class()
                                ][0]["doc_uuid"],
                                chunk_retrieval_results["data"]["Get"][
                                    embedder.get_chunk_class()
                                ][0]["chunk_id"],
                            )
                            added_chunks[str(_range)] = chunk_obj

            for chunk in added_chunks:                    
                if chunk not in doc_name_map[doc]:
                    doc_name_map[doc][chunk] = added_chunks[chunk]

        for doc in doc_name_map:
            sorted_Dict = {
                k: doc_name_map[doc][k]
                for k in sorted(doc_name_map[doc], key=lambda x: int(x))
            }

            for value in sorted_Dict.values():
                context += value.text

        return context
