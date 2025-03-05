from typing import List, Tuple
from typing import Dict, List, Tuple, Union
from model.interfaces import IDocumentModel
from observer.interfaces import IObserver, IPublisher


class ComparisonModel(IPublisher):
    """
    A specialized DocumentModel for managing comparison text.
    """

    def __init__(self):
        super().__init__()
        self._documents: List[IDocumentModel] = []
        self._file_names: List[str] = []
        self._merged_text: str = ""
        self._comparison_sentences = []
        self._current_index = 0

    def set_documents(self, documents: List[IDocumentModel]) -> None:
        """
        Sets the list of documents and updates the file names.

        This method updates the internal document list and ensures that the file names
        are stored accordingly. It also notifies observers about the changes.

        Args:
            documents (List[IDocumentModel]): The list of document models.
        """
        self._documents = documents
        self._file_names = [document.get_file_name() for document in documents]
        # This triggers the construction of the corresponding displays
        self.notify_observers()

    def register_comparison_displays(self, observers: List[IObserver]) -> None:
        """
        Registers observers for the documents.

        This method assigns an observer to each document to track updates and changes. 
        The number of documents and observers must match.

        Args:
            observers (List[IObserver]): The list of observers.

        Raises:
            ValueError: If the number of documents and observers does not match.
        """
        if len(self._documents)+1 != len(observers):
            raise ValueError(
                f"Mismatch between number of documents ({len(self._documents)+1}) and observers ({len(observers)})")
        for document, observer in zip(self._documents, observers):
            document.add_observer(observer)

    def set_comparison_data(self, comparison_data: Dict[str, Union[str, List[Tuple[str, ...]]]]) -> None:
        """
        Sets the comparison data including common text and sentence comparisons.

        Args:
            comparison_data (Dict[str, Union[str, List[Tuple[str, ...]]]]): 
                A dictionary containing:
                - "common_text" (str): The shared text across comparisons.
                - "comparison_sentences" (List[Tuple[str, ...]]): A list of sentence tuples,
                where each tuple contains a variable number of strings.
        """
        self._merged_text = comparison_data["common_text"]
        self._comparison_sentences = comparison_data["comparison_sentences"]
        self._current_index = 0
        self.notify_observers()

    def next_sentence(self) -> None:
        """
        Advances to the next sentence tuple in the comparison sentences list.
        If at the last element, it wraps around to the first element.
        If the current element has been removed, it automatically moves to the next available element.
        """
        if not self._comparison_sentences:
            return  # No sentences available

        # Move to next index, wrapping around if necessary
        self._current_index = (self._current_index +
                               1) % len(self._comparison_sentences)

        self._update_document_texts()

    def previous_sentence(self) -> None:
        """
        Moves to the previous sentence tuple in the comparison sentences list.
        If at the first element, it wraps around to the last element.
        If the current element has been removed, it automatically moves to the next available element.
        """
        if not self._comparison_sentences:
            return  # No sentences available

        # Move to previous index, wrapping around if necessary
        self._current_index = (self._current_index -
                               1) % len(self._comparison_sentences)

        self._update_document_texts()

    def remove_current_sentence(self) -> None:
        """
        Removes the currently selected sentence tuple from the comparison sentences list.
        After removal, it moves to the next available sentence.
        If the last element is removed, it wraps around to the first element.
        If the list becomes empty, no further action is taken.
        """
        if not self._comparison_sentences:
            return  # No sentences available

        # Remove the current sentence
        del self._comparison_sentences[self._current_index]

        # Handle case where list becomes empty after removal
        if not self._comparison_sentences:
            self._current_index = 0  # Reset index, but nothing to navigate
            return

        # Ensure index remains valid after removal
        self._current_index %= len(self._comparison_sentences)

        self._update_document_texts()

    def _update_document_texts(self) -> None:
        """
        Updates the text of each document in self._documents with the corresponding sentence
        from the current tuple in self._comparison_sentences.

        Assumes that self._current_index is set correctly.
        """
        if not self._comparison_sentences:
            return  # No sentences to update

        sentence_tuple: Tuple[str, ...] = self._comparison_sentences[self._current_index]

        for document, sentence in zip(self._documents, sentence_tuple):
            document.set_text(sentence)

    def get_state(self) -> Dict[str, int]:
        """
        Returns the current state of the comparison model.

        This method provides metadata about the comparison process, including 
        the total number of sentence tuples and the current index of the active sentence.

        Returns:
            Dict[str, int]: A dictionary containing:
                - "num_sentences" (int): The total number of sentence tuples available.
                - "current_sentence_index" (int): The index of the currently selected sentence tuple.
        """
        return {"file_names": self._file_names,
                "num_sentences": len(self._comparison_sentences),
                "current_sentence_index": self._current_index}
