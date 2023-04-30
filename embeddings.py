from langchain.document_loaders import(
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.text_splitter import CharacterTextSplitter
import openai
from dotenv import load_dotenv
import os
from chatgpt import search_gpt

load_dotenv()

#Load Langchain variables
openai.api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings()
llm = OpenAI(temperature=0)
text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=25)
vectorstore ='docs/index'
new_vectorstore = ''

def change_vectorstore(optional_arg="new_vectorstore"):
    global vectorstore
    global new_vectorstore
    if not new_vectorstore:
        return vectorstore
    else:
        vectorstore = new_vectorstore
    print(vectorstore)
    return vectorstore

#Check if the files are valid
def check_file(file_path):
    if file_path.endswith('.txt'):
        loader = TextLoader(file_path)
        print("txt file loaded")
        return loader.load()
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        print("pdf file loaded")
        return loader.load()
    if file_path.endswith('.md'):
        loader = UnstructuredMarkdownLoader(file_path)
        return loader.load()
        print("md file loaded")
    else:
        return Exception('Invalid file type')

#Format text
def base_formatter(docs):
    print(f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))
    return (f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))

#Loop files in a folder path for embedding
def create_mass_embedding(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt' or '.pdf' or '.md'):
            file_path=os.path.join(folder_path, filename)
            create_embedding(file_path)
        else:
            return Exception("No Valid files found in folder")
    else:
        return Exception("No files found in folder")


#Embed a single embedding
def create_embedding(file_path):
    data = check_file(file_path)
    base_formatter(data)
    vectorstore = change_vectorstore()
    chromadb = Chroma.from_documents(data, embeddings, persist_directory=vectorstore)
    chromadb.persist()
    return "Embedding created"

#Load vectorstore database
def load_embedding():
    vectorstore = change_vectorstore()
    chromadb = Chroma(persist_directory=vectorstore, embedding_function=embeddings)
    return chromadb

#Search for uncompressed docs in database
def base_retriever(user_query):
    retriever = load_embedding().as_retriever(llm=llm)
    docs = retriever.get_relevant_documents(user_query)
    return base_formatter(docs)

#Search for compressed docs in database
def retriever(user_query):
    compressor = LLMChainExtractor.from_llm(llm)
    retriever = load_embedding().as_retriever(llm=llm)
    cc_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
    compressed_docs = cc_retriever.get_relevant_documents(user_query)
    docs = base_formatter(compressed_docs)
    return docs

#Query the database and pass the info to chatgpt for response
def memory_search(user_query):
    data = base_retriever(user_query)
    prompt = [{
        "role":"system",
        "content":'''
        "The user has asked this question:

        {user_query}

        You have looked up the relevant information from your data store and it is:

        {data}

        Please answer the user's question using the data as relevant context."
        '''.format(user_query=user_query, data=data)
    }]

    result = search_gpt(user_query, prompt)

    return result