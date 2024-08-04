"""
PDF Reader that handles ORC of PDF files. Based on Weaviate's Verba
https://github.com/weaviate/Verba
"""
import base64
import glob
import os
from datetime import datetime
from pathlib import Path
from PyPDF2 import PdfReader
from wasabi import msg
from typing_extensions import List, Optional
from loguru import logger

from src.vectordb.readers.document import Document
from src.vectordb.readers.interface import InputForm, Reader


class PDFReader(Reader):
    """
    The PDFReader reads .pdf files using Unstructured. It can handle both paths, content and bites. Requires the PyPDF2 library.
    """

    def __init__(self):
        """
        Initializes the PDFReader object with the necessary file types, required libraries, name, description, and input form.
        """
        super().__init__()
        self.file_types = [".pdf"]
        self.requires_library = ["PyPDF2"]
        self.name = "PDFReader"
        self.description = "Reads PDF files using the PyPDF2 library"
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
        Ingest data into Weaviate
        @parameter: bites : List[str] - List of bites
        @parameter: contents : List[str] - List of string content
        @parameter: paths : List[str] - List of paths to files
        @parameter: file_names : List[str] - List of file names
        @parameter: document_type : str - Document type
        @returns List[Document] - Lists of documents.
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
                    data_path = Path(path)
                    if data_path.exists():
                        if data_path.is_file():
                            documents += self.load_file(data_path, document_type)
                        else:
                            documents += self.load_directory(data_path, document_type)
                    else:
                        msg.warn(f"Path {data_path} does not exist")

        # If bites exist
        if len(bites) > 0 and len(bites) == len(file_names):
            for byte, file_name in zip(bites, file_names):
                decoded_bites = base64.b64decode(byte)
                with open(f"{file_name}", "wb") as file:
                    file.write(decoded_bites)

                documents += self.load_file(Path(file_name), document_type)
                os.remove(f"{file_name}")

        # If content exist
        if len(contents) > 0 and len(contents) == len(file_names):
            for content, file_name in zip(contents, file_names):
                document = Document(
                    name=file_name,
                    text=content,
                    doc_type=document_type,
                    timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    reader=self.name,
                )
                documents.append(document)

        logger.info(f"Loaded {len(documents)} documents")
        return documents

    def load_file(self, file_path: Path, document_type: str) -> List[Document]:
        """
        Loads a PDF file and returns a list of Document objects.

        Args:
            file_path (Path): The path to the PDF file to be loaded.
            document_type (str): The type of document to load.

        Returns:
            List[Document]: A list of Document objects loaded from the PDF file.

        This function loads a PDF file based on the provided file path and returns a list of Document objects.
        It creates a PdfReader object from the file_path and extracts the full text from all the pages of the PDF.
        It then creates a Document object with the extracted text, document type, name, link, timestamp, and reader name.
        The created Document object is added to a list of documents.
        Finally, it logs a success message and returns the list of documents.
        """
        reader = PdfReader(file_path)

        full_text = "".join(page.extract_text() + "\n\n" for page in reader.pages)
        document = Document(
            text=full_text,
            doc_type=document_type,
            name=str(file_path),
            link=str(file_path),
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        documents = [document]
        logger.info(f"Loaded {str(file_path)}")
        return documents

    def load_directory(self, dir_path: Path, document_type: str) -> List[Document]:
        """
        Loads documents from a directory and its subdirectories.

        Args:
            dir_path (Path): The path to the directory.
            document_type (str): The type of the documents.

        Returns:
            List[Document]: A list of Document objects representing the loaded documents.

        This function initializes an empty list to store the documents. It then converts the `dir_path` to a string if it is a Path object.

        Next, it loops through each file type specified in `self.file_types`. For each file type, it uses the `glob` module to find all the files in `dir_path` and its subdirectories that match the current file type.

        For each file found, it logs a message indicating that it is reading the file. It then opens the file in read mode with UTF-8 encoding. It calls the `load_file` method with the file path and the specified `document_type`, and appends the returned documents to the `documents` list.

        Finally, it logs a success message indicating the number of documents loaded and returns the list of documents.
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
                logger.info(f"Reading {str(file)}")
                with open(file, encoding="utf-8"):
                    documents += self.load_file(Path(file), document_type=document_type)

        logger.info(f"Loaded {len(documents)} documents")
        return documents
