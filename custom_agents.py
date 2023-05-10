from embeddings import load_vector_store_docs, embeddings
from langchain.agents import initialize_agent, load_tools, Tool
from dotenv import load_dotenv
from chatgpt import search_gpt
from langchain import OpenAI, Wikipedia
from langchain.utilities import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, load_tools, Tool
from langchain.agents import AgentType
from langchain.agents.react.base import DocstoreExplorer
docstore = DocstoreExplorer(Wikipedia())

llm = OpenAI(temperature=0)

tools = [
    Tool(
        name="Search",
        func=docstore.search,
        description="useful for when you need to ask with search"
    ),
    Tool(name="Lookup",
         func=docstore.lookup,
         description="useful for when you need to ask with lookup"
         )
]

load_dotenv()

vectorstore = load_vector_store_docs()


def base_retriever(user_query):
    retriever = embeddings.embed_query(text=user_query)
    docs = vectorstore.similarity_search_by_vector(
        embedding=retriever, top_k=1)
    print(docs)
    return docs


def data_base_memory_search(user_query):
    docs = base_retriever(user_query)
    print(docs)
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

    result = search_gpt(prompt)

    print("Memory search result: " + result)

    return result
