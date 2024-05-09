"""
Github Reader. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""

import base64
import json
import os
import requests
from datetime import datetime
from wasabi import msg
from typing_extensions import List, Tuple, Optional
from loguru import logger

from src.vectordb.readers.document import Document
from src.vectordb.readers.interface import InputForm, Reader


class GithubReader(Reader):
    """
    The GithubReader downloads files from Github and ingests them into Weaviate.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the GithubReader class.

        This constructor sets up the initial state of the GithubReader object by assigning values to its instance variables. It calls the constructor of the parent class using the `super()` function. The `name` variable is set to "GithubReader", indicating the name of the reader. The `requires_env` variable is set to a List containing the required environment variable "GITHUB_TOKEN". The `description` variable is set to a string describing the functionality of the GithubReader, indicating that it downloads only text files from a GitHub repository and ingests them into Verba, and provides the format for specifying the repository, owner, and folder. The `input_form` variable is set to the value of `InputForm.INPUT.value`, indicating that the reader expects input in the form of a specific input.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.name = "GithubReader"
        self.requires_env = ["GITHUB_TOKEN"]
        self.description = "Downloads only text files from a GitHub repository and ingests it into Verba. Use this format {owner}/{repo}/{folder}"
        self.input_form = InputForm.INPUT.value

    def load(
        self,
        bites: Optional[List[str]] = None,
        contents: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
        file_names: Optional[List[str]] = None,
        document_type: str = "Documentation",
    ) -> List[Document]:
        """
        Load documents from the given paths, contents, bites, and file names.

        Parameters:
            bites (Optional[List[str]]): A list of base64-encoded strings representing data. Defaults to None.
            contents (Optional[List[str]]): A list of strings containing document contents. Defaults to None.
            paths (Optional[List[str]]): A list of file paths to load data from. Defaults to None.
            file_names (Optional[List[str]]): A list of file names corresponding to the paths. Defaults to None.
            document_type (str): The type of document to load. Defaults to "Documentation".

        Returns:
            List[Document]: A list of Document objects loaded from the data sources.
        """
        if file_names is None:
            file_names = []
        if paths is None:
            paths = []
        if contents is None:
            contents = []
        if bites is None:
            bites = []
        documents = []

        # If paths exist
        if len(paths) > 0:
            for path in paths:
                if path != "":
                    files = self.fetch_docs(path)

                    for _file in files:
                        try:
                            content, link, _path = self.download_file(path, _file)
                        except TypeError as e:
                            logger.warning(f"Couldn't load, skipping {_file}: {str(e)}")
                            continue

                        if ".json" in _file:
                            json_obj = json.loads(str(content))
                            try:
                                document = Document.from_json(json_obj)
                            except Exception as e:
                                raise ValueError(f"Loading JSON failed {e}") from e

                        else:
                            document = Document(
                                text=content,
                                type=document_type,
                                name=_file,
                                link=link,
                                path=_path,
                                timestamp=str(
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                ),
                                reader=self.name,
                            )
                        documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents

    def fetch_docs(self, path: str) -> List:
        """
        Fetches documents based on the given path from a GitHub repository.

        Parameters:
            path (str): The path to fetch documents from in the format owner/repo.

        Returns:
            List: A list of file paths for the fetched documents.
        """
        split = path.split("/")
        owner = split[0]
        repo = split[1]
        folder_path = "/".join(split[2:]) if len(split) > 2 else ""
        # Path should be owner/repo
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        response = self.call_download_file(url)
        files = [
            item["path"]
            for item in response.json()["tree"]
            if item["path"].startswith(folder_path)
            and (
                item["path"].endswith(".md")
                or item["path"].endswith(".mdx")
                or item["path"].endswith(".txt")
                or item["path"].endswith(".json")
            )
        ]
        msg.info(
            f"Fetched {len(files)} file_names from {url} (checking folder {folder_path})"
        )
        return files

    def download_file(self, path: str, file_path: str) -> Tuple[str, str, str]:
        """
        Download files from Github based on file_name.

        Parameters:
            path (str): The path to a GitHub repository.
            file_path (str): The path of the file in the repository.

        Returns:
            str: The content of the file.

        Raises:
            None
        """
        split = path.split("/")
        owner = split[0]
        repo = split[1]

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        response = self.call_download_file(url)
        content_b64 = response.json()["content"]
        link = response.json()["html_url"]
        path = response.json()["path"]
        content = base64.b64decode(content_b64).decode("utf-8")
        logger.info(f"Downloaded {url}")
        return (content, link, path)

    def call_download_file(self, url) -> requests.Response:
        """
        Downloads a file from the given URL using the Github API.

        Args:
            url (str): The URL of the file to download.

        Returns:
            requests.Response: The response object containing the downloaded file.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returns an error status code.

        """
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}",
            "Accept": "application/vnd.github.v3+json",
        }
        result = requests.get(url, headers=headers, timeout=30)
        result.raise_for_status()
        return result
