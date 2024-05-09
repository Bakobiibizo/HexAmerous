"""
Simple Retriever. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
from typing_extensions import List, Tuple
from weaviate.client import Client
from weaviate.hybrid import HybridFusion

from src.vectordb.retrievers.interface import Retriever
from src.vectordb.embedders.interface import Embedder
from src.vectordb.chunkers.chunk import Chunk


class SimpleRetriever(Retriever):
    """
    SimpleRetriver that retrieves chunks through hybrid search, no reranking or additional logic.
    """

    def __init__(self):
        super().__init__()
        self.description = "SimpleRetriever uses Hybrid Search to retrieve relevant chunks to the user's query"
        self.name = "SimpleRetriever"

    def retrieve(
        self,
        queries: List[str],
        client: Client,
        embedder: Embedder,
    ) -> Tuple[List[Chunk], str]:
        """Ingest data into Weaviate
        @parameter: queries : List[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns List[Chunk] - List of retrieved chunks.
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

        context = "".join(f"{chunk.text} " for chunk in sorted_chunks)
        return sorted_chunks, context
