from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from ye_logger_of_yor import get_logger
from chatgpt import search_gpt
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from embeddings import load_vector_store_docs
from langchain.schema import Document

logger = get_logger()

embedding = OpenAIEmbeddings()
llm = OpenAI()
vectorstore = load_vector_store_docs()

# Search for uncompressed docs in database
logger.info('base_retriever function')


def base_retriever(user_query):
    logger.info('running base_retriever')
    retriever = SelfQueryRetriever.from_llm(llm, vectorstore, document_content_description="programming", verbose=True)
    retriever.get_relevant_documents(query=user_query)


# Search for compressed docs in database
logger.info('retriever function')


def retriever(user_query):
    logger.info('running retriever')
    retriever = base_retriever(user_query)
    compressor = load_vector_store_docs().as_compressor(llm=llm)
    logger.info(compressor)
    return docs


def memory_search(user_query):
    logger.info('running memory_search')
    data = base_retriever(user_query)
    prompt = [{
        "role": "system",
        "content": '''
        "The user has asked this question:

        {user_query}

        You have looked up the relevant information from your data store and it is:

        {data}

        Please answer the user's question using the data as relevant context."
        '''.format(user_query=user_query, data=data)
    }]

    result = search_gpt(user_query, prompt)

    logger.info(msg=f"Memory search result: {result}")

    return result
