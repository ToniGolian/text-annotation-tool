from typing import List, Dict
from model.interfaces import IDocumentModel
from model.interfaces import ITagModel


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
        self._filename: str = ""
        self._meta_tags: Dict = {}
        self._text: str = ""

    # Getters and Setters

    def get_filename(self) -> str:
        """
        Retrieves the filename of the document.

        Returns:
            str: The filename of the document.
        """
        return self._filename

    def set_filename(self, file_name: str) -> None:
        """
        Sets the filename of the document.

        Args:
            file_name (str): The filename to be set.
        """
        self._filename = file_name
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

    def get_data_state(self) -> dict:
        """
        Retrieves a dictionary representation of the object's attributes.

        The dictionary includes the following attributes:
            - "filename": The name of the file associated with the object.
            - "meta_tags": The metadata tags associated with the object.
            - "text": The textual content managed by the object.

        Returns:
            dict: A dictionary containing the object's attributes as keys and their corresponding values.
        """
        return {"filename": self._filename,
                "meta_tags": self._meta_tags,
                "text": self._text}
