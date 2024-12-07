from abc import ABC, abstractmethod
from observer.interfaces import IDataPublisher, ILayoutPublisher


class ITagModel(ABC):
    pass


class IComparisonModel(IDataPublisher, ILayoutPublisher):
    pass


class IConfigurationModel(ILayoutPublisher):
    pass


class IDocumentModel(IDataPublisher):
    pass

    @abstractmethod
    def get_text(self) -> str:
        """
        Retrieves the text content of the document.

        Returns:
            str: The current text content of the document.
        """
        pass

    @abstractmethod
    def set_text(self, text: str) -> None:
        """
        Updates the text content of the document.

        Args:
            text (str): The new text content to set in the document.
        """
        pass
