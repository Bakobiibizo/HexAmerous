# -*- coding: utf-8 -*-
from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.text_splitter import TokenTextSplitter
import openai
from dotenv import load_dotenv
import os
from chatgpt import search_gpt
from ye_logger_of_yor import get_logger

logger = get_logger()

load_dotenv()

logger.info('Loading global variables')
# Load Langchain variables
openai.api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings()
llm = OpenAI(temperature=0)
vectorstore_location = './docs/'
text_splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=25)


logger.info('base_formatter function')


def base_formatter(docs):
    logger.info('formatting')
    logger.info(f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" +
                                         d.page_content for i, d in enumerate(docs)]))
    return (f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))


logger.info('loading check_file function 43')
# Check if the files are valid


def check_file(file_path):
    logger.info('checking file')
    if file_path.endswith('.txt'):
        loader = TextLoader(file_path)
        logger.info(loader.load())
        return loader.load()
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        logger.info("pdf file loaded")
        return loader.load()
    if file_path.endswith('.md'):
        loader = UnstructuredMarkdownLoader(file_path)
        logger.info(loader.load())
        return loader.load()
    else:
        logger.info("File type not supported")
        return "File type not supported"


logger.info('loading create_mass_embedding function')
# Loop files in a folder path for embedding


def create_mass_embedding(folder_path):
    logger.info('creating mass embedding')
    if not os.path.exists(folder_path):
        folder_path = 'docs/empty'
        result = "Folder does not exist"
        logger.info(result)
        return
    else:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            result = create_embedding(file_path, filename)
            logger.info(f"Embedding created for {filename}: {result}")
            with open('docs.txt', 'a') as f:
                f.write(f"{os.path.join(folder_path, file_path)}\n")
            logger.info(f"Embedding created for {filename}: {result}")

        return result


logger.info('create_embedding function')
# Embed a single embedding


def create_embedding(file_path, optional_arg="metadata"):
    logger.info('creating embedding')
    data = check_file(file_path)
    metadata = optional_arg
    if metadata:
        meta = metadata
    else:
        meta = 'file_path'

    data = text_splitter.split_documents(documents=data)
    vectordb = Chroma.from_documents(
        documents=data, metadata=meta, embedding=embeddings, persist_directory=vectorstore_location)
    vectordb.persist()
    return "Embedding created"

logger.info('load_vector_store_docs function')


def load_vector_store_docs():
    logger.info('running load_vector_store_docs')
    docs = Chroma(persist_directory=vectorstore_location,
                  embedding_function=embeddings)
    logger.info(docs)
    return docs


logger.info('memory_search function')
# Query the database and pass the info to chatgpt for response
