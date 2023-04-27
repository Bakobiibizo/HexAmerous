from langchain.document_loaders import(
    TextLoader,
    PyPDFLoader
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()

llm = OpenAI(temperature=0)

def check_file(file_path):
    if file_path.endswith('.txt'):
        loader = TextLoader(file_path)
        return loader.load()
    elif file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        return loader.load()
    else:
        raise Exception('Invalid file type')

def base_formatter(docs):
    print(f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))
    return (f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))

def create_mass_embedding(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path=os.path.join(folder_path, filename)
            create_embedding(file_path)
        else:
            raise Exception("No PDFs found in folder")

def create_embedding(file_path):
    data = check_file(file_path)
    base_formatter(data)
    vectordb = Chroma.from_documents(data, embeddings, persist_directory='docs/langchain')
    vectordb.persist()
    return vectordb

def load_embedding():
    vectordb = Chroma(persist_directory='docs/langchain', embedding_function=embeddings)
    return vectordb

def base_retriever(user_query):
    retriever = load_embedding().as_retriever(llm=llm, search_kwars={"k":1})
    docs = retriever.get_relevant_documents(user_query)
    return base_formatter(docs)

def retriever(user_query):
    compressor = LLMChainExtractor.from_llm(llm)
    retriever = load_embedding().as_retriever(llm=llm)
    cc_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
    compressed_docs = cc_retriever.get_relevant_documents(user_query)
    docs = base_formatter(compressed_docs)
    return docs
