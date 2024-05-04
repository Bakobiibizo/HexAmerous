from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import SpladeEncoder
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone import Pinecone
import time
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embed = OpenAIEmbeddings(
    model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY, dimensions=768
)

PINE_API_KEY = os.getenv("PINE_API_KEY")

index_name = "splade"

pc = Pinecone(api_key=PINE_API_KEY)

index = pc.Index(index_name)
# wait a moment for connection
time.sleep(0.2)

splade_encoder = SpladeEncoder()

text_field = "text"

retriever1 = PineconeHybridSearchRetriever(
    embeddings=embed,
    sparse_encoder=splade_encoder,
    index=index,
    namespace="UFL",
    top_k=3,
)
