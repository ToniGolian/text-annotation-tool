import hashlib
from pprint import pprint
from typing import List, Tuple
from typing import Dict, List, Tuple, Union
from model.annotation_document_model import AnnotationDocumentModel
from model.interfaces import IDocumentModel
from observer.interfaces import IObserver, IPublisher


class ComparisonModel(IPublisher):
    """
    A specialized DocumentModel for managing comparison text.
    """

    def __init__(self):
        super().__init__()
        self._document_models: List[IDocumentModel] = []
        self._file_names: List[str] = []
        self._merged_text_model: IDocumentModel = None
        self._comparison_sentences: List[str] = []
        self._differing_to_global: Dict[int:int] = {}
        self._current_sentence_hash: str = ""
        self._current_index: int = 0

    def set_documents(self, documents: List[IDocumentModel]) -> None:
        """
        Sets the list of documents and updates the file names.

        This method updates the internal document list and ensures that the file names
        are stored accordingly. It also notifies observers about the changes.

        Args:
            documents (List[IDocumentModel]): The list of document models.
        """
        self._document_models = documents
        self._file_names = [document.get_file_name() for document in documents]

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
        if len(self._document_models) != len(observers):
            raise ValueError(
                f"Mismatch between number of documents ({len(self._document_models)}) and observers ({len(observers)})")
        for document_model, observer in zip(self._document_models, observers):
            document_model.add_observer(observer)

    def set_comparison_data(self, comparison_data: Dict[str, Union[str, List[Tuple[str, ...]], Dict[str, int]]]) -> None:
        """
        Sets the comparison data including common text, differing sentences, and index mapping.

        Args:
            comparison_data (Dict[str, Union[str, List[Tuple[str, ...]], Dict[int, int]]]):
                A dictionary containing:
                - "common_text" (str): The full merged reference text.
                - "comparison_sentences" (List[Tuple[str, ...]]): A list of sentence tuples where each tuple
                  contains one sentence per annotator and the first item is the unannotated base version.
                - "differing_to_global" (Dict[int, int]): A mapping from the local index in the differing
                  sentence list to the corresponding index in the global merged text.
        """
        self._merged_text_model = comparison_data["merged_text_model"]
        self._comparison_sentences = comparison_data["comparison_sentences"]
        self._differing_to_global = comparison_data["differing_to_global"]
        self._current_index = 0
        self.notify_observers()
        self._update_document_texts()

    def next_sentence(self) -> None:
        """
        Advances to the next sentence index in the comparison sentences list.
        If at the last index, it wraps around to the first index.
        If the current element has been removed, it automatically moves to the next available element.
        """
        if not self._comparison_sentences or not self._comparison_sentences[0]:
            return  # No sentences available

        # Move to next index, wrapping around if necessary
        self._current_index = (self._current_index +
                               1) % len(self._comparison_sentences[0])

        self._update_document_texts()

    def previous_sentence(self) -> None:
        """
        Moves to the previous sentence index in the comparison sentences list.
        If at the first index, it wraps around to the last index.
        If the current element has been removed, it automatically moves to the next available element.
        """
        if not self._comparison_sentences or not self._comparison_sentences[0]:
            return  # No sentences available

        # Move to previous index, wrapping around if necessary
        self._current_index = (self._current_index -
                               1) % len(self._comparison_sentences[0])

        self._update_document_texts()

    def remove_current_sentence(self) -> None:
        """
        Removes the currently selected sentence across all lists in the comparison sentences.
        After removal, it moves to the next available sentence.
        If the last element is removed, it wraps around to the first element.
        If the list becomes empty, no further action is taken.
        """
        if not self._comparison_sentences or not self._comparison_sentences[0]:
            return  # No sentences available

        # Remove the current sentence from all sublists
        for sentence_list in self._comparison_sentences:
            del sentence_list[self._current_index]

        # Handle case where sentences become empty after removal
        if not self._comparison_sentences[0]:
            self._current_index = 0  # Reset index, but nothing to navigate
            self._update_document_texts()
        else:
            # Ensure index remains valid after removal
            self._current_index %= len(self._comparison_sentences[0])
        self._update_document_texts()

    def _update_document_texts(self) -> None:
        """
        Updates the text of each document in self._documents with the corresponding sentence
        from the current index in the comparison sentences list.

        Assumes that self._current_index is set correctly.
        """
        if not self._comparison_sentences or not self._comparison_sentences[0]:
            # Important: Notify observers with empty state
            self._document_models[0].set_text("NO MORE DIFFERING SENTENCES.")
            for document in self._document_models[1:]:
                document.set_text("")
            self.notify_observers()
            return

        # Extract the current sentence for each document
        sentence_list = [sentence[self._current_index]
                         for sentence in self._comparison_sentences]

        for document, sentence in zip(self._document_models, sentence_list):
            document.set_text(sentence)
        self.notify_observers()

        # Calc the hash for the current sentence
        self._current_sentence_hash = hashlib.md5(
            sentence_list[0].encode("utf-8")).hexdigest()

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
        num_sentences = len(
            self._comparison_sentences[0]) if self._comparison_sentences else 0
        return {"file_names": self._file_names,
                "num_sentences": num_sentences,
                "current_sentence_index": self._current_index}

    def adopt_sentence(self, adoption_index: int) -> None:
        """
        Returns the sentence variant at the current index for the given annotator 
        and leaves the model unchanged.

        Args:
            adoption_index (int): The index of the annotation variant to adopt 
                                  (0 = raw, >0 = annotated).

        Returns:
            str: The selected sentence variant.
        """
        adoption_sentence = self._comparison_sentences[adoption_index][self._current_index]
        global_index = self._differing_to_global[self._current_sentence_hash]
        self._merged_text_model[global_index] = adoption_sentence
        self.remove_current_sentence()
