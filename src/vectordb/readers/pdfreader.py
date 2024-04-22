import base64
import glob
import os
from datetime import datetime
from pathlib import Path

from wasabi import msg

from goldenverba.components.reader.document import Document
from goldenverba.components.reader.interface import InputForm, Reader

try:
    from PyPDF2 import PdfReader
except Exception:
    msg.warn("PyPDF2 not installed, your base installation might be corrupted.")


class PDFReader(Reader):
    """
    The PDFReader reads .pdf files using Unstructured.
    """

    def __init__(self):
        super().__init__()
        self.file_types = [".pdf"]
        self.requires_library = ["PyPDF2"]
        self.name = "PDFReader"
        self.description = "Reads PDF files using the PyPDF2 library"
        self.input_form = InputForm.UPLOAD.value

    def load(
        self,
        bites: List[str] = None,
        contents: List[str] = None,
        paths: List[str] = None,
        file_names: List[str] = None,
        document_type: str = "Documentation",
    ) -> List[Document]:
        """Ingest data into Weaviate
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
            for byte, fileName in zip(bites, file_names):
                decoded_bites = base64.b64decode(byte)
                with open(f"{fileName}", "wb") as file:
                    file.write(decoded_bites)

                documents += self.load_file(f"{fileName}", document_type)
                os.remove(f"{fileName}")

        # If content exist
        if len(contents) > 0 and len(contents) == len(file_names):
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

    def load_file(self, file_path: Path, document_type: str) -> List[Document]:
        """Loads .pdf file
        @param file_path : Path - Path to file
        @param document_type : str - Document Type
        @returns List[Document] - Lists of documents.
        """
        documents = []
        full_text = ""
        reader = PdfReader(file_path)

        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"

        document = Document(
            text=full_text,
            type=document_type,
            name=str(file_path),
            link=str(file_path),
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        documents.append(document)
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
                    documents += self.load_file(file, document_type=document_type)

        msg.good(f"Loaded {len(documents)} documents")
        return documents