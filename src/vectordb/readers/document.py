"""
Document class for Vectordb. Based on Weaviate's Verba.
https://github.com/weaviate/Verba
"""
from typing_extensions import List, Dict, Optional

from src.vectordb.chunkers.chunk import Chunk


class Document:
    """
    Document class. Standard document for data ingestion into Vectordb.
    """
    def __init__(
        self,
        text: Optional[str] = "",
        doc_type: Optional[str] = "",
        name: Optional[str] = "",
        path: Optional[str] = "",
        link: Optional[str] = "",
        timestamp: Optional[str] = "",
        reader: Optional[str] = "",
        meta: Optional[Dict] = None,
    ):
        """
        Initializes a new instance of the Document class.

        Args:
            text (str): The text of the document. Defaults to an empty string.
            doc_type (str): The doc_type of the document. Defaults to an empty string.
            name (str): The name of the document. Defaults to an empty string.
            path (str): The path of the document. Defaults to an empty string.
            link (str): The link of the document. Defaults to an empty string.
            timestamp (str): The timestamp of the document. Defaults to an empty string.
            reader (str): The reader of the document. Defaults to an empty string.
            meta (Dict): Additional metadata of the document. Defaults to an empty dictionary.

        Returns:
            None
        """
        if meta is None:
            meta = {}
        self._text = text
        self._doc_type = doc_type
        self._name = name
        self._path = path
        self._link = link
        self._timestamp = timestamp
        self._reader = reader
        self._meta = meta
        self.chunks: List[Chunk] = []

    @property
    def text(self):
        """
        Get the text property of the object.

        Returns:
            str: The text property of the object.
        """
        return self._text

    @property
    def doc_type(self):
        """
        Get the doc_type property of the object.

        Returns:
            str: The doc_type property of the object.
        """
        return self._doc_type

    @property
    def name(self):
        """
        Get the name property of the object.

        Returns:
            str: The name property of the object.
        """
        return self._name

    @property
    def path(self):
        """
        Get the path property of the object.

        Returns:
            str: The path property of the object.
        """
        return self._path

    @property
    def link(self):
        """
        Get the link property of the object.

        Returns:
            str: The link property of the object.
        """
        return self._link

    @property
    def timestamp(self):
        """
        Get the timestamp property of the object.

        Returns:
            str: The timestamp property of the object.
        """
        return self._timestamp

    @property
    def reader(self):
        """
        Get the reader property of the object.

        Returns:
            The reader property of the object.
        """
        return self._reader

    @property
    def meta(self):
        """
        Get the meta property of the object.

        Returns:
            The meta property of the object.
        """
        return self._meta

    @staticmethod
    def to_json(document) -> Dict:
        """
        Convert the Document object to a JSON dictionary.

        Args:
            document: The Document object to be converted.

        Returns:
            A JSON dictionary representing the Document object.
        """
        return {
            "text": document.text,
            "doc_type": document.doc_type,
            "name": document.name,
            "path": document.path,
            "link": document.link,
            "timestamp": document.timestamp,
            "reader": document.reader,
            "meta": document.meta,
            "chunks": [chunk.to_Dict() for chunk in document.chunks],
        }

    @staticmethod
    def from_json(doc_Dict: Dict):
        """
        Convert a JSON string to a Document object.

        Args:
            doc_Dict (Dict): A dictionary containing the JSON string.

        Returns:
            Document: A Document object created from the JSON string.
        """
        document = Document(
            text=doc_Dict.get("text", ""),
            doc_type=doc_Dict.get("doc_type", ""),
            name=doc_Dict.get("name", ""),
            path=doc_Dict.get("path", ""),
            link=doc_Dict.get("link", ""),
            timestamp=doc_Dict.get("timestamp", ""),
            reader=doc_Dict.get("reader", ""),
            meta=doc_Dict.get("meta", {}),
        )
        # Assuming Chunk has a from_dict method
        document.chunks = [
            Chunk.from_dict(chunk_data) for chunk_data in doc_Dict.get("chunks", [])
        ]
        return document