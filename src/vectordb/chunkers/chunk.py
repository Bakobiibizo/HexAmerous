"""
Chunk. Based off of Weaviate's Verba.
https://github.com/weaviate/Verba
"""

from typing_extensions import Dict


class Chunk:
    "Chunk class that represents a chunk of text."

    def __init__(
        self,
        text: str = "",
        doc_name: str = "",
        doc_type: str = "",
        doc_uuid: str = "",
        chunk_id: str = "",
    ):
        """
        Initializes a new instance of the Chunk class.

        Args:
            text (str): The text of the chunk. Defaults to an empty string.
            doc_name (str): The name of the document containing the chunk. Defaults to an empty string.
            doc_type (str): The type of the document containing the chunk. Defaults to an empty string.
            doc_uuid (str): The UUID of the document containing the chunk. Defaults to an empty string.
            chunk_id (str): The ID of the chunk. Defaults to an empty string.
        """
        self._text = text
        self._doc_name = doc_name
        self._doc_type = doc_type
        self._doc_uuid = doc_uuid
        self._chunk_id = chunk_id
        self._text_no_overlap = text
        self._tokens = 0
        self._vector = None
        self._score = 0

    @property
    def text(self):
        """
        Returns the value of the `_text` attribute.

        :return: The value of the `_text` attribute.
        :rtype: str
        """
        return self._text

    @property
    def text_no_overlap(self):
        """
        Returns the value of the `_text_no_overlap` attribute.

        :return: The value of the `_text_no_overlap` attribute.
        :rtype: str
        """
        return self._text_no_overlap

    @property
    def doc_name(self):
        """
        Get the name of the document.

        :return: The name of the document.
        :rtype: str
        """
        return self._doc_name

    @property
    def doc_type(self):
        """
        Get the doc_type property of the object.

        Returns:
            str: The doc_type property of the object.
        """
        return self._doc_type

    @property
    def doc_uuid(self):
        """
        Returns the value of the `_doc_uuid` attribute.

        :return: The value of the `_doc_uuid` attribute.
        :rtype: str
        """
        return self._doc_uuid

    @property
    def chunk_id(self):
        """
        Get the chunk ID of the object.

        :return: The chunk ID of the object.
        :rtype: str
        """
        return self._chunk_id

    @property
    def tokens(self):
        """
        Returns the value of the `_tokens` attribute.
        """
        return self._tokens

    @property
    def vector(self):
        """
        Returns the value of the `_vector` attribute.

        :return: The value of the `_vector` attribute.
        """
        return self._vector

    @property
    def score(self):
        """
        Get the score property of the object.

        Returns:
            The score property of the object.
        """
        return self._score

    def set_uuid(self, uuid):
        """
        Sets the UUID of the document.

        Parameters:
            uuid (str): The UUID to set.

        Returns:
            None
        """
        self._doc_uuid = uuid

    def set_tokens(self, token):
        """
        Sets the value of the `_tokens` attribute.

        Parameters:
            token (any): The token to set.

        Returns:
            None
        """
        self._tokens = token

    def set_vector(self, vector):
        """
        Set the vector attribute of the object.

        Args:
            vector: The vector to set.

        Returns:
            None
        """
        self._vector = vector

    def set_score(self, score):
        """
        Set the score of the object.

        Parameters:
            score (any): The score to set.

        Returns:
            None
        """
        self._score = score

    def to_dict(self) -> Dict:
        """
        Convert the Chunk object to a Dictionary.
        """
        return {
            "text": self.text,
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "doc_uuid": self.doc_uuid,
            "chunk_id": self.chunk_id,
            "tokens": self.tokens,
            "vector": self.vector,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Construct a Chunk object from a Dictionary."""
        chunk = cls(
            text=data.get("text", ""),
            doc_name=data.get("doc_name", ""),
            doc_type=data.get("doc_type", ""),
            doc_uuid=data.get("doc_uuid", ""),
            chunk_id=data.get("chunk_id", ""),
        )
        chunk.set_tokens(data.get("tokens", 0))
        chunk.set_vector(data.get("vector"))
        chunk.set_score(data.get("score", 0))
        return chunk
