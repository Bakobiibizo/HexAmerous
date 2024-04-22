"""
UnstructuredPDF Reader. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
import base64
import glob
import os
from datetime import datetime
from pathlib import Path

import requests
from wasabi import msg
from typing_extensions import List, Optional

from vectordb.reader.document import Document
from vectordb.reader.interface import InputForm, Reader


class UnstructuredPDF(Reader):
    """
    UnstructuredPDF Reader that handles ORC of PDF files. Does require an API key from https://unstructured.io/api-key-hosted. Should be included in your .env file as UNSTRUCTURED_API_KEY.
    """
    def __init__(self):
        """
        Initializes an instance of the UnstructuredPDF class.

        This method initializes the attributes of the UnstructuredPDF class, including the file types,
        required environment variables, name, description, and input form.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.file_types = [".pdf"]
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "UnstructuredPDF"
        self.description = "Reads PDF files powered by unstructured.io"
        self.input_form = InputForm.UPLOAD.value

    def load(
        self,
        bites: Optional[List[str]] = None,
        contents: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
        file_names: Optional[List[str]] = None,
        document_type: str = "Documentation",
    ) -> List[Document]:
        """
        Load the content from the provided paths, bites, or contents and return a List of Document objects.

        Args:
            bites (List[str], optional): A List of byte strings representing the content to be loaded. Defaults to None.
            contents (List[str], optional): A List of strings representing the content to be loaded. Defaults to None.
            paths (List[str], optional): A List of file paths representing the files to be loaded. Defaults to None.
            file_names (List[str], optional): A List of strings representing the names of the files to be loaded. Defaults to None.
            document_type (str, optional): The type of the document. Defaults to "Documentation".

        Returns:
            List[Document]: A List of Document objects representing the loaded content.

        Raises:
            None

        Examples:
            >>> reader = UnstructuredPDF()
            >>> documents = reader.load(paths=["/path/to/file.pdf"])
            >>> documents = reader.load(bites=["bites_string"], file_names=["file.pdf"])
            >>> documents = reader.load(contents=["content_string"], file_names=["file.txt"])
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
        if paths:
            for path in paths:
                if path != "":
                    data_path = Path(path)
                    if data_path.exists():
                        if data_path.is_file():
                            documents += self.load_file(data_path, document_type)
                        else:
                            documents += self.load_directory(data_path, document_type)
                    else:
                        msg.warn(f"Path {data_path} does not exist")

        # If bites exist
        if bites and len(bites) == len(file_names):
            for byte, fileName in zip(bites, file_names):
                documents += self.load_bites(byte, fileName, document_type)

        # If content exist
        if contents and len(contents) == len(file_names):
            for content, fileName in zip(contents, file_names):
                document = Document(
                    name=fileName,
                    text=content,
                    type=document_type,
                    timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    reader=self.name,
                )
                documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents

    def load_bites(self, bites_string, fileName, document_type: str) -> List[Document]:
        """
        Loads the content from the provided `bites_string` by decoding it, making a POST request to the `UNSTRUCTURED_API_URL` with the decoded content, and processing the response to create a Document object. The created Document is returned in a List. 

        Parameters:
            bites_string: A string containing the content to be loaded.
            fileName: The name of the file.
            document_type: The type of the document.

        Returns:
            A List containing a single Document object.
        """
        url = os.environ.get(
            "UNSTRUCTURED_API_URL", "https://api.unstructured.io/general/v0/general"
        )

        headers = {
            "accept": "application/json",
            "unstructured-api-key": os.environ.get("UNSTRUCTURED_API_KEY", ""),
        }

        data = {
            "strategy": "auto",
        }

        decoded_bites = base64.b64decode(bites_string)
        with open("reconstructed.pdf", "wb") as file:
            file.write(decoded_bites)

        file_data = {"files": open("reconstructed.pdf", "rb")}

        response = requests.post(url, headers=headers, data=data, files=file_data, timeout=30)

        json_response = response.json()

        full_content = ""

        for chunk in json_response:
            if "text" in chunk:
                text = chunk["text"]
                full_content += f"{text} "

        document = Document(
            text=full_content,
            type=document_type,
            name=str(fileName),
            link=str(fileName),
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        documents = [document]
        msg.good(f"Loaded {str(fileName)}")
        os.remove("reconstructed.pdf")
        return documents

    def load_file(self, file_path: Path, document_type: str) -> List[Document]:
        """
        Load a file and return a List of Document objects.

        Args:
            file_path (Path): The path to the file to be loaded.
            document_type (str): The type of the document.

        Returns:
            List[Document]: A List of Document objects representing the loaded file.
        """
        if file_path.suffix not in self.file_types:
            msg.warn(f"{file_path.suffix} not supported")
            return []

        url = os.environ.get(
            "UNSTRUCTURED_API_URL", "https://api.unstructured.io/general/v0/general"
        )

        headers = {
            "accept": "application/json",
            "unstructured-api-key": os.environ.get("UNSTRUCTURED_API_KEY", ""),
        }

        data = {
            "strategy": "auto",
        }

        file_data = {"files": open(file_path, "rb")}

        response = requests.post(url, headers=headers, data=data, files=file_data, timeout=30)

        file_data["files"].close()

        json_response = response.json()

        full_content = ""

        for chunk in json_response:
            if "text" in chunk:
                text = chunk["text"]
                full_content += f"{text} "

        document = Document(
            text=full_content,
            type=document_type,
            name=str(file_path),
            link=str(file_path),
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        documents = [document]
        msg.good(f"Loaded {str(file_path)}")
        return documents

    def load_directory(self, dir_path: Path, document_type: str) -> List[Document]:
        """Loads .pdf files from a directory and its subdirectories.

        @param dir_path : Path - Path to directory
        @param document_type : str - Document Type
        @returns List[Document] - List of documents
        """
        # Initialize an empty Dictionary to store the file contents
        documents = []

        # Convert dir_path to string, in case it's a Path object
        dir_path_str = str(dir_path)

        # Loop through each file type
        for file_type in self.file_types:
            # Use glob to find all the files in dir_path and its subdirectories matching the current file_type
            files = glob.glob(f"{dir_path_str}/**/*{file_type}", recursive=True)

            # Loop through each file
            for file in files:
                msg.info(f"Reading {str(file)}")
                with open(file, encoding="utf-8"):
                    documents += self.load_file(Path(file), document_type=document_type)

        msg.good(f"Loaded {len(documents)} documents")
        return documents