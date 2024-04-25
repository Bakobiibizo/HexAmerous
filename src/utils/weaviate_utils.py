import weaviate
import weaviate.classes as wvc
import os
from typing import List

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

weaviate_client = weaviate.connect_to_wcs(
    cluster_url=WEAVIATE_URL,
    auth_credentials=None,
    headers={
        "X-OpenAI-Api-Key": OPENAI_API_KEY,
    },
)


def retrieve_file_chunks(file_ids: List[str], query: str) -> List[str]:
    collection = None
    try:
        collection = weaviate_client.collections.get(name="opengpts")
    except Exception:
        collection = weaviate_client.collections.create(
            name="opengpts",
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
        )

    retrieve_file_chunks = collection.query.near_text(
        query=query,
        limit=2,
        filters=wvc.query.Filter.by_property("file_id").contains_any(file_ids),
    )
    print("RETRIEVE FILE CHUNKS: ", retrieve_file_chunks)

    chunks = [
        chunk.properties["text"] for chunk in retrieve_file_chunks.objects
    ]

    return chunks
