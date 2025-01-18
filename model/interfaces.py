from abc import ABC, abstractmethod
from typing import Dict
from observer.interfaces import IDataPublisher, ILayoutPublisher


class ITagModel(ABC):
    pass


class IComparisonModel(IDataPublisher, ILayoutPublisher):
    pass


class IConfigurationModel(ILayoutPublisher):
    pass


class IDocumentModel(IDataPublisher):
    """
    Interface for a document model that manages metadata, text, and associated tags.
    """

    @abstractmethod
    def get_filename(self) -> str:
        """
        Retrieves the filename of the document.

        Returns:
            str: The filename of the document.
        """
        pass

    @abstractmethod
    def set_filename(self, file_name: str) -> None:
        """
        Sets the filename of the document.

        Args:
            file_name (str): The filename to be set.
        """
        pass

    @abstractmethod
    def get_meta_tags(self) -> Dict:
        """
        Retrieves the meta tags associated with the document.

        Returns:
            dict: A dictionary containing the meta tags.
        """
        pass

    @abstractmethod
    def set_meta_tags(self, metatags: Dict) -> None:
        """
        Sets the meta tags associated with the document.

        Args:
            metatags (dict): A dictionary containing the meta tags to set.
        """
        pass

    @abstractmethod
    def get_text(self) -> str:
        """
        Retrieves the text content of the document.

        Returns:
            str: The text content of the document.
        """
        pass

    @abstractmethod
    def set_text(self, text: str) -> None:
        """
        Sets the text content of the document.

        Args:
            text (str): The new text content to set.
        """
        pass

    @abstractmethod
    def set_document(self, document: Dict) -> None:
        """
        Updates the document model with new data.

        This method sets the filename, meta tags, and text of the document model
        based on the provided dictionary.

        Args:
            document (dict): A dictionary containing the document data with the following keys:
                - "filename" (str): The name of the file.
                - "meta_tags" (dict): Metadata tags associated with the document.
                - "text" (str): The text content of the document.
        """
        pass

    @abstractmethod
    def get_data_state(self) -> Dict:
        """
        Retrieves a dictionary representation of the object's attributes.

        The dictionary includes the following attributes:
            - "filename": The name of the file associated with the object.
            - "meta_tags": The metadata tags associated with the object.
            - "text": The textual content managed by the object.

        Returns:
            dict: A dictionary containing the object's attributes as keys and their corresponding values.
        """
        pass


class ISelectionModel(IDataPublisher):
    """
    Interface for the SelectionModel, defining methods to manage and retrieve the selected text.
    """

    @abstractmethod
    def set_selected_text(self, text: str) -> None:
        """
        Sets the currently selected text and notifies observers.

        Args:
            text (str): The newly selected text.
        """
        pass

    @abstractmethod
    def get_data_state(self) -> Dict[str, str]:
        """
        Retrieves the current selected text as a dictionary.

        Returns:
            Dict[str, str]: A dictionary containing the selected text.
        """
        pass
