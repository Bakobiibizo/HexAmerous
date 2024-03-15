from embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any, Callable, List

load_dotenv()

from chatgpt import openai

embeddings = OpenAIEmbeddings()



search_tool = Tool(
    name='search',
    function=base_retriever,
    description='useful for when you need to answer questions about current events'
)

load_dotenv()

metadata_field_info=[
    AttributeInfo(
        name='README.md',
        description='readme file for the hexamerous project',
        type='string or list[string]'
    )
]

document_content_description = 'a readme file from a python project called hexamerous.'

def base_retriever(user_query):
    vectorstore = load_vector_store_docs()
    retriever = SelfQueryRetriever.from_llm(llm, vectorstore, document_content_description, metadata_field_info, verbose=True)
    docs = retriever.get_relevant_documents(user_query)
    print(docs)
    return docs




def data_base_memory_search(user_query):
    docs = base_retriever(user_query)
    prompt = {
        "role": "system",
        "content": '''
        "The user has asked this question:

        {query}

        You have looked up the relevant information from your data store and it is:

        {data}

        Please answer the user's question using the data as relevant context."
        '''.format(query=user_query, data=docs)
    }
    print(prompt)

    result = chat_gpt(prompt)

    print(f"Memory search result: {result}")

    return result
