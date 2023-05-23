# -*- coding: utf-8 -*-
from langchain.document_loaders import PlaywrightURLLoader, SitemapLoader
from langchain.text_splitter import TextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from embeddings import create_embedding, load_vector_store_docs
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders.sitemap import SitemapLoader
import nest_asyncio

# Load Langchain variables
embeddings = OpenAIEmbeddings()
text_splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=25)
# Scrape a website


def scrape_site(url):

    urls = [
        str(url)
    ]

    # File loader/scraper
    loader = PlaywrightURLLoader(
        urls=urls, remove_selectors=["header", "footer"])
    raw_data = loader.load()
    data = raw_data[0].page_content

    # Text splitter
    texts = text_splitter.split_text(data, chunk_size=300, chunk_overlap=25)
    print(texts)

    create_embedding(texts)


def scrape_site_map(site_path, collection_name=None):

    nest_asyncio.apply()

    sitemap_loader = SitemapLoader(web_path=site_path)

    docs = sitemap_loader.load()

    # Store in database
    metadata = collection_name
    meta = metadata or 'file_path'
    create_embedding(docs)
