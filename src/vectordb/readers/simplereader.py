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

from vectordb.reader.document import Document
from vectordb.reader.interface import InputForm, Reader


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
        bites: List[str] = None,
        contents: List[str] = None,
        paths: List[str] = None,
        file_names: List[str] = None,
        document_type: str = "Documentation",
    ) -> List[Document]:
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
                try:
                    original_text = decoded_bites.decode("utf-8")
                except UnicodeDecodeError:
                    msg.fail(
                        f"Error decoding text for file {fileName}. The file might not be a text file."
                    )
                    continue

                if ".json" in fileName:
                    json_obj = json.loads(original_text)
                    try:
                        document = Document.from_json(json_obj)
                    except Exception as e:
                        raise Exception(f"Loading JSON failed {e}")

                else:
                    document = Document(
                        name=fileName,
                        text=original_text,
                        type=document_type,
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )
                documents.append(document)

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
                    raise Exception(f"Loading JSON failed {e}")

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