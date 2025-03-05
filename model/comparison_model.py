from typing import List
from model.interfaces import IDocumentModel
from observer.interfaces import IObserver, IPublisher


class ComparisonModel(IPublisher):
    """
    A specialized DocumentModel for managing comparison text.
    """

    def __init__(self):
        super().__init__()
        self._documents: List[IDocumentModel] = []
        self._merged_text: str = ""
        self._comparison_sentences = []

    def set_documents(self, documents: List[IDocumentModel], observers: List[IObserver]) -> None:
        """
        Associates each document with an observer and ensures the count matches.

        Args:
            documents (List[IDocumentModel]): The list of document models.
            observers (List[IObserver]): The list of observers.

        Raises:
            ValueError: If the number of documents and observers does not match.
        """
        if len(documents) != len(observers):
            raise ValueError(
                f"Mismatch between number of documents ({len(documents)}) and observers ({len(observers)})"
            )

        self._documents = documents
        for document, observer in zip(documents, observers):
            document.add_observer(observer)

    def get_state(self) -> list:
        """
        Retrieves the tags associated with the document.

        Returns:
            list: A list of tags represented as ITagModel objects.
        """
        state = {}
        return state
