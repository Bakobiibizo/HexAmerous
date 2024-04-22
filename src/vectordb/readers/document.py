from goldenverba.components.chunking.chunk import Chunk


class Document:
    def __init__(
        self,
        text: str = "",
        type: str = "",
        name: str = "",
        path: str = "",
        link: str = "",
        timestamp: str = "",
        reader: str = "",
        meta: Dict = None,
    ):
        if meta is None:
            meta = {}
        self._text = text
        self._type = type
        self._name = name
        self._path = path
        self._link = link
        self._timestamp = timestamp
        self._reader = reader
        self._meta = meta
        self.chunks: List[Chunk] = []

    @property
    def text(self):
        return self._text

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def link(self):
        return self._link

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def reader(self):
        return self._reader

    @property
    def meta(self):
        return self._meta

    @staticmethod
    def to_json(document) -> Dict:
        """Convert the Document object to a JSON Dict."""
        doc_Dict = {
            "text": document.text,
            "type": document.type,
            "name": document.name,
            "path": document.path,
            "link": document.link,
            "timestamp": document.timestamp,
            "reader": document.reader,
            "meta": document.meta,
            "chunks": [chunk.to_Dict() for chunk in document.chunks],
        }
        return doc_Dict

    @staticmethod
    def from_json(doc_Dict: Dict):
        """Convert a JSON string to a Document object."""
        document = Document(
            text=doc_Dict.get("text", ""),
            type=doc_Dict.get("type", ""),
            name=doc_Dict.get("name", ""),
            path=doc_Dict.get("path", ""),
            link=doc_Dict.get("link", ""),
            timestamp=doc_Dict.get("timestamp", ""),
            reader=doc_Dict.get("reader", ""),
            meta=doc_Dict.get("meta", {}),
        )
        # Assuming Chunk has a from_Dict method
        document.chunks = [
            Chunk.from_Dict(chunk_data) for chunk_data in doc_Dict.get("chunks", [])
        ]
        return document