from abc import ABC, abstractmethod
from typing import Dict, List
from observer.interfaces import IPublisher, IPublisher


class ITagModel(ABC):
    pass


class IComparisonModel(IPublisher):
    pass


class IConfigurationModel(IPublisher):
    @abstractmethod
    def get_color_scheme(self) -> Dict[str, str]:
        """
        Retrieves the current color scheme of the application.

        This method returns a dictionary containing the color scheme settings
        used in the application. The color scheme typically defines UI colors
        such as background, foreground, and highlight colors.

        Returns:
            Dict: A dictionary mapping UI elements to their corresponding colors.
        """
        pass


class IDocumentModel(IPublisher):
    """
    Interface for a document model that manages metadata, and text.
    """

    @abstractmethod
    def get_file_name(self) -> str:
        """
        Retrieves the file_name of the document.

        Returns:
            str: The file_name of the document.
        """
        pass

    @abstractmethod
    def set_file_name(self, file_name: str) -> None:
        """
        Sets the file_name of the document.

        Args:
            file_name (str): The file_name to be set.
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

        This method sets the file_name, meta tags, and text of the document model
        based on the provided dictionary.

        Args:
            document (dict): A dictionary containing the document data with the following keys:
                - "file_name" (str): The name of the file.
                - "meta_tags" (dict): Metadata tags associated with the document.
                - "text" (str): The text content of the document.
        """
        pass

    @abstractmethod
    def get_state(self) -> Dict:
        """
        Retrieves a dictionary representation of the object's attributes.

        The dictionary includes the following attributes:
            - "file_name": The name of the file associated with the object.
            - "meta_tags": The metadata tags associated with the object.
            - "text": The textual content managed by the object.

        Returns:
            dict: A dictionary containing the object's attributes as keys and their corresponding values.
        """
        pass


class IAnnotableDocumentModel(IDocumentModel):
    """
    Interface for a document model that manages metadata, text, and associated tags.
    """
    @abstractmethod
    def get_tags(self) -> List[ITagModel]:
        """
        Retrieves the tag list of the document.

        Returns:
            List[ITagModel]: The tag list of the document.
        """
        pass

    @abstractmethod
    def set_tags(self, tags: List[ITagModel]) -> None:
        """
        Sets the tag list of the document.

        Args:
            tags (List[ITagModel]): The list of tags to set.
        """
        pass


class ISelectionModel(IPublisher):
    """
    Interface for the SelectionModel, defining methods to manage and retrieve the selected text.
    """

    @abstractmethod
    def set_selected_text_data(self, selected_data: Dict) -> None:
        """
        Sets the currently selected text and notifies observers.

        Args:
            text (str): The newly selected text.
        """
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, str]:
        """
        Retrieves the current selected text as a dictionary.

        Returns:
            Dict[str, str]: A dictionary containing the selected text.
        """
        pass
