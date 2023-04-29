from langchain.document_loaders import PlaywrightURLLoader
from langchain.text_splitter import TextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from embeddings import create_embedding, load_embedding, base_formatter
from langchain.text_splitter import TokenTextSplitter

#Scrape a website
def scrape_site(url):

    #Load Langchain variables
    embeddings = OpenAIEmbeddings()
    text_splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=25)
    urls = [
        str(url)
    ]

    #File loader/scraper
    loader = PlaywrightURLLoader(urls=urls, remove_selectors=["header", "footer"])
    raw_data = loader.load()
    data = raw_data[0].page_content

    #Text splitter
    texts = text_splitter.split_text(data)
    print(texts)

    #Store in database
    vectordb = Chroma.from_texts(texts, embeddings, persist_directory='docs/index')
    vectordb.persist()

    return vectordb
