from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from src.helpers.datastax_vectordb import (
    ASTRA_DB_KEYSPACE,
    session
)


"""
Initialize a vectorstore database to act as memory. Has a 1 hour memeory buffer and then the data in the buffer is cleared. Commit important data before that time elapses.
"""
message_history = CassandraChatMessageHistory(
    session_id = "anything",
    session=session,
    keyspace = ASTRA_DB_KEYSPACE,
    ttl_seconds = 3600
)
message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)