"""
xml sitemap web scraper. Enter the sitemap url in the cli and press enter. If you want a filter enter it into docs/regex_filter.txt in regex format.
"""
import loguru
import nest_asyncio
from langchain.document_loaders.sitemap import SitemapLoader
from bs4 import BeautifulSoup
from typing import Optional, List


logger = loguru.logger

def parse_xml_data(content: BeautifulSoup) -> str:
    # Find all 'nav' and 'header' elements in the BeautifulSoup object
    labels = content.find_all("tr", {"class": "even"})
    items = content.find_all("tr", {"class": "odd"})

    # Remove each 'nav' and 'header' element from the BeautifulSoup object
    for element in labels + items:
        element.decompose()

    return str(content.get_text())

def sitemap_loader(map_filter: Optional[List[str]]=None, data_path: Optional[str]=None): 
    if not data_path:
        data_path = "./docs/ingestion/data.txt"
    nest_asyncio.apply()
    map_filter = map_filter or get_filter()

    logger.debug([data_path, map_filter])
    url = input("Enter XML Sitemap URL: ")
    if not url.startswith("http"):
        url = f"http://{url}"
    map_loader = SitemapLoader(
        web_path=url,
        parsing_function=parse_xml_data
        )


    docs = map_loader.load()

    map_loader.requests_per_second = 2
    # Optional: avoid `[SSL: CERTIFICATE_VERIFY_FAILED]` issue
    map_loader.requests_kwargs = {"verify": False}

    with open(data_path, "a", encoding="utf-8") as file:
        for doc in docs:
            file.write(f"{doc}\n")
            return data_path

def get_filter():
    with open("docs/regex_filter.txt", "r", encoding="utf-8") as file:
        return file.readlines()
    
def main(regex: Optional[List[str]], final_data_path="./docs/ingestion/data.txt"):
    if not regex:
        regex = get_filter()
    url_filter=regex
    if not final_data_path:
        final_data_path = "./docs/ingestion/data.txt"
    
    
    data = sitemap_loader(map_filter=url_filter, data_path="./docs/ingestion/data.txt")
    print(data)
    
    
    

if __name__ == "__main__":
    regex_filter = get_filter()
    sitemap_loader(map_filter=regex_filter, data_path="./docs/ingestion/data.txt")