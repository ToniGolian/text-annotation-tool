from typing import List, Dict, Tuple
from model.interfaces import IDocumentModel, ITagModel


class DocumentModel(IDocumentModel):
    """
    Represents a document model that encapsulates the document's metadata,
    text, and associated tags.
    """

    def __init__(self):
        """
        Initializes the DocumentModel with default values for its attributes.
        """
        super().__init__()
        self._document_type = ""
        self._file_path: str = ""
        self._file_name: str = ""
        self._meta_tags: Dict = {}
        self._text: str = ""

    # Getters and Setters

    def get_file_name(self) -> str:
        """
        Retrieves the filename of the document.

        Returns:
            str: The filename of the document.
        """
        return self._file_name

    def set_file_name(self, file_name: str) -> None:
        """
        Sets the filename of the document.

        Args:
            file_name (str): The filename to be set.
        """
        self._file_name = file_name
        self.notify_data_observers()

    def get_file_path(self) -> str:
        """
        Retrieves the file_path of the document.

        Returns:
            str: The file_path of the document.
        """
        return self._file_path

    def set_file_path(self, file_path: str) -> None:
        """
        Sets the file_path of the document.

        Args:
            file_path (str): The file_path to be set.
        """
        self._file_path = file_path
        self.notify_data_observers()

    def get_meta_tags(self) -> dict:
        """
        Retrieves the meta tags associated with the document.

        Returns:
            dict: A dictionary containing the meta tags.
        """
        return self._meta_tags

    def set_meta_tags(self, metatags: dict) -> None:
        """
        Sets the meta tags associated with the document.

        Args:
            metatags (dict): A dictionary containing the meta tags to set.
        """
        self._meta_tags = metatags
        self.notify_data_observers()

    def get_text(self) -> str:
        """
        Retrieves the text content of the document.

        Returns:
            str: The text content of the document.
        """
        return self._text

    def set_text(self, text: str) -> None:
        """
        Sets the text content of the document.

        Args:
            text (str): The new text content to set.
        """
        self._text = text
        self.notify_data_observers()

    def get_document_type(self) -> str:
        """
        Retrieves the document type.

        Returns:
            str: The type of the document.
        """
        return self._document_type

    def set_document_type(self, document_type: str) -> None:
        """
        Sets the document type.

        Args:
            document_type (str): The type of the document to set.
        """
        self._document_type = document_type

    def get_highlight_data(self) -> List[Tuple[str, int, int]]:
        """
        Retrieves the current highlight data.

        Returns:
            List[Tuple[str, int, int]]: A list of tuples where each tuple consists of:
                - The tag type (str).
                - The start position of the tag in the text (int).
                - The end position of the tag in the text (int).
        """
        return self._highlight_data

    def set_highlight_data(self, highlight_data: List[Tuple[str, int, int]]) -> None:
        """
        Sets the highlight data.

        Args:
            highlight_data (List[Tuple[str, int, int]]): A list of tuples where each tuple consists of:
                - The tag type (str).
                - The start position of the tag in the text (int).
                - The end position of the tag in the text (int).
        """
        self._highlight_data = highlight_data

    def set_document(self, document: dict) -> None:
        """
        Updates the document model with new data.

        This method sets the document type, file path, filename, meta tags, 
        and text of the document model based on the provided dictionary.

        Args:
            document (dict): A dictionary containing the document data with the following keys:
                - "document_type" (str): The type of the document (e.g., "annotation", "comparison").
                - "file_path" (str): The full path to the file.
                - "filename" (str): The name of the file.
                - "meta_tags" (dict): Metadata tags associated with the document.
                - "text" (str): The text content of the document.

        Updates:
            - Sets the internal attributes for document type, file path, filename, meta tags, and text.
            - Notifies all registered data observers about the changes.
        """
        self._document_type = document["document_type"]
        self._file_path: str = document["file_path"]
        self._file_name = document["filename"]
        self._meta_tags = document["meta_tags"]
        self._text = document["text"]
        self.notify_data_observers()

    def get_data_state(self) -> dict:
        """
        Retrieves a dictionary representation of the object's attributes.

        The dictionary includes the following attributes:
            - "file_path": The path, where the document is stored.
            - "filename": The name of the file associated with the object.
            - "meta_tags": The metadata tags associated with the object.
            - "text": The textual content managed by the object.

        Returns:
            dict: A dictionary containing the object's attributes as keys and their corresponding values.
        """
        return {"document_type": self._document_type,
                "file_path": self._file_path,
                "filename": self._file_name,
                "meta_tags": self._meta_tags,
                "text": self._text}
