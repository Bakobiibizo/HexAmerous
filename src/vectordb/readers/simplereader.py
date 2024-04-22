"""
Simple Reader for .txt, .md, .mdx, and .json files. Based on Weaviate's Verba,
https://github.com/weaviate/Verba
"""
import base64
import glob
import json
from datetime import datetime
from pathlib import Path
from wasabi import msg
from typing_extensions import List, Optional

from src.vectordb.readers.document import Document
from src.vectordb.readers.interface import InputForm, Reader


class SimpleReader(Reader):
    """
    The SimpleReader reads .txt, .md, .mdx, and .json files. It can handle both paths, content and bites.
    """
    def __init__(self):
        """
        Initializes a new instance of the SimpleReader class.

        This constructor sets up the initial state of the SimpleReader object by assigning values to its instance variables. It calls the constructor of the parent class using the `super()` function. The `file_types` variable is set to a List of file extensions that the SimpleReader can handle, which includes ".txt", ".md", ".mdx", and ".json". The `name` variable is set to "SimpleReader", indicating the name of the reader. The `description` variable is set to "Reads text, markdown, and json files.", providing a brief description of the reader's functionality. Finally, the `input_form` variable is set to the value of `InputForm.UPLOAD`, indicating that the reader expects input in the form of file uploads.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.file_types = [".txt", ".md", ".mdx", ".json"]
        self.name = "SimpleReader"
        self.description = "Reads text, markdown, and json files."
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
        Loads data from various sources and returns a list of Document objects.

        Parameters:
            bites (List[str]): A list of base64-encoded strings representing data.
            contents (List[str]): A list of strings containing document contents.
            paths (List[str]): A list of file paths to load data from.
            file_names (List[str]): A list of file names corresponding to the paths.
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

        # If bytes exist
        if bites and len(bites) == len(file_names):
            for byte, file_name in zip(bites, file_names):
                decoded_bites = base64.b64decode(byte)
                try:
                    original_text = decoded_bites.decode("utf-8")
                except UnicodeDecodeError:
                    msg.fail(
                        f"Error decoding text for file {file_name}. The file might not be a text file."
                    )
                    continue

                if ".json" in file_name:
                    json_obj = json.loads(original_text)
                    try:
                        document = Document.from_json(json_obj)
                    except Exception as e:
                        raise ValueError(f"Loading JSON failed {e}") from e

                else:
                    document = Document(
                        name=file_name,
                        text=original_text,
                        type=document_type,
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )
                documents.append(document)

        # If content exist
        if contents and len(contents) == len(file_names):
            for content, file_name in zip(contents, file_names):
                document = Document(
                    name=file_name,
                    text=content,
                    type=document_type,
                    timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    reader=self.name,
                )
                documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents

    def load_file(self, file_path: Path, document_type: str) -> List[Document]:
        """
        Loads a file and returns a list of Document objects.

        Args:
            file_path (Path): The path to the file to be loaded.
            document_type (str): The type of document to load.

        Returns:
            List[Document]: A list of Document objects loaded from the file.

        Raises:
            Exception: If loading the JSON file fails.

        This function loads a file based on the provided file path and returns a list of Document objects.
        It first checks if the file extension is supported by the reader. If not, it logs a warning message and returns an empty list.
        If the file extension is supported, it opens the file in read mode with UTF-8 encoding.
        If the file is a JSON file, it loads the JSON object and creates a Document object from it.
        If the file is not a JSON file, it reads the entire file content and creates a Document object with the file content, document type, name, link, timestamp, and reader name.
        The created Document object is added to the list of documents.
        Finally, it logs a success message and returns the list of documents.
        """
        documents = []

        if file_path.suffix not in self.file_types:
            msg.warn(f"{file_path.suffix} not supported")
            return []

        with open(file_path, encoding="utf-8") as f:
            msg.info(f"Reading {str(file_path)}")

            if file_path.suffix == ".json":
                json_obj = json.loads(f.read())
                try:
                    document = Document.from_json(json_obj)
                except Exception as e:
                    raise ValueError(f"Loading JSON failed {e}") from e

            else:
                document = Document(
                    text=f.read(),
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
        """
        Loads documents from a directory and its subdirectories.

        Args:
            dir_path (Path): The path to the directory.
            document_type (str): The type of the documents.

        Returns:
            List[Document]: A list of Document objects representing the loaded documents.

        This function initializes an empty list to store the documents. It then converts the `dir_path` to a string if it is a Path object. 

        Next, it loops through each file type specified in `self.file_types`. For each file type, it uses the `glob` module to find all the files in `dir_path` and its subdirectories that match the current file type.

        For each file found, it logs a message indicating that it is reading the file. It then opens the file in read mode with UTF-8 encoding. It creates a `Document` object with the file's contents, the specified `document_type`, the file's name and link, the current timestamp, and the name of the reader. The `Document` object is added to the `documents` list.

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
                msg.info(f"Reading {str(file)}")
                with open(file, encoding="utf-8") as f:
                    document = Document(
                        text=f.read(),
                        type=document_type,
                        name=str(file),
                        link=str(file),
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )

                    documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents