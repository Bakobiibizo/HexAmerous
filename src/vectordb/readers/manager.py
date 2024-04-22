from wasabi import msg

from goldenverba.components.reader.document import Document
from goldenverba.components.reader.githubreader import GithubReader
from goldenverba.components.reader.interface import Reader
from goldenverba.components.reader.pdfreader import PDFReader
from goldenverba.components.reader.simplereader import SimpleReader
from goldenverba.components.reader.unstructuredpdf import UnstructuredPDF


class ReaderManager:
    def __init__(self):
        self.readers: Dict[str, Reader] = {
            "SimpleReader": SimpleReader(),
            "PDFReader": PDFReader(),
            "GithubReader": GithubReader(),
            "UnstructuredPDF": UnstructuredPDF(),
        }
        self.selected_reader: Reader = self.readers["SimpleReader"]

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
        return self.selected_reader.load(
            bites, contents, paths, file_names, document_type
        )

    def set_reader(self, reader: str) -> bool:
        if reader in self.readers:
            self.selected_reader = self.readers[reader]
            return True
        else:
            msg.warn(f"Reader {reader} not found")
            return False

    def get_readers(self) -> Dict[str, Reader]:
        return self.readers