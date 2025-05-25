import hashlib
from pprint import pprint
from typing import List, Tuple
from typing import Dict, List, Tuple, Union
from model.interfaces import IComparisonModel, IDocumentModel, ITagModel
from observer.interfaces import IObserver, IPublisher


class ComparisonModel(IComparisonModel):
    """
    A specialized DocumentModel for managing comparison text.
    """

    def __init__(self):
        super().__init__()
        self._document_models: List[IDocumentModel] = []
        self._file_names: List[str] = []
        self._merged_document: IDocumentModel = None
        self._comparison_sentences: List[List[str]] = []
        self._adopted_flags: List[int] = []
        self._differing_to_global: List[int] = []
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
        self._merged_document = comparison_data["merged_document"]
        self._comparison_sentences = comparison_data["comparison_sentences"]
        self._adopted_flags: List[int] = [
            False for _ in self._comparison_sentences]
        self._differing_to_global = comparison_data["differing_to_global"]
        self._unresolved_references: List[ITagModel] = []
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

    # def remove_current_sentence(self) -> None:
    #     """
    #     Removes the currently selected sentence across all lists in the comparison sentences.
    #     After removal, it moves to the next available sentence.
    #     If the last element is removed, it wraps around to the first element.
    #     If the list becomes empty, no further action is taken.
    #     """
    #     if not self._comparison_sentences or not self._comparison_sentences[0]:
    #         return  # No sentences available

    #     # Remove the current sentence from all sublists
    #     for sentence_list in self._comparison_sentences:
    #         del sentence_list[self._current_index]

    #     # Handle case where sentences become empty after removal
    #     if not self._comparison_sentences[0]:
    #         self._current_index = 0  # Reset index, but nothing to navigate
    #         self._update_document_texts()
    #     else:
    #         # Ensure index remains valid after removal
    #         self._current_index %= len(self._comparison_sentences[0])
    #     self._update_document_texts()
    #     return

    def mark_sentence_as_adopted(self, adopted_index: int = None) -> int:
        """
        Marks the specified sentence as adopted (processed), or the current one if no index is given.

        If all sentences are adopted after this operation, the views are updated with a final message.
        Otherwise, the next unadopted sentence is selected.

        Args:
            adopted_index (int, optional): The index of the sentence to mark as adopted.
                                        Defaults to the currently active sentence.

        Returns:
            int: The index of the sentence that was marked as adopted.
        """
        if not self._comparison_sentences or not self._comparison_sentences[0]:
            return -1  # No valid sentence to mark

        if not adopted_index:
            adopted_index = self._current_index
        self._adopted_flags[adopted_index] = True

        # Find the next unadopted sentence
        total = len(self._adopted_flags)
        next_index = (adopted_index + 1) % total

        while next_index != adopted_index and self._adopted_flags[next_index]:
            next_index = (next_index + 1) % total

        if self._adopted_flags[next_index]:
            # All sentences adopted
            for i, doc in enumerate(self._document_models):
                doc.set_text("NO MORE DIFFERING SENTENCES." if i == 0 else "")
            self.notify_observers()
        else:
            self._current_index = next_index
            self._update_document_texts()

        return adopted_index

    def unmark_sentence_as_adopted(self, index: int) -> None:
        """
        Reverts the adoption state of the sentence at the given index.

        This method clears the adopted flag for the specified sentence, marking it
        as not yet processed.

        Args:
            index (int): The index of the sentence to unmark.

        Raises:
            IndexError: If the index is out of bounds.
        """
        if index < 0 or index >= len(self._adopted_flags):
            raise IndexError(f"Invalid sentence index {index} for unmarking.")

        self._adopted_flags[index] = False

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

    def update_comparison_sentences(self) -> None:
        """
        Synchronizes the raw comparison sentence with the current content of the raw document model.

        It uses the global sentence index to identify the sentence from the merged text,
        and replaces the corresponding entry in self._comparison_sentences[0]
        if the sentence has been modified.
        """
        self._comparison_sentences[0][self._current_index] = self._document_models[0].get_text(
        )

    def get_state(self) -> dict:
        """
        Returns the serialized state of the comparison model for saving.

        The returned dictionary is compatible with perform_save_as() and includes
        the merged document's content as well as information needed to reconstruct
        the comparison later.

        Returns:
            dict: A dictionary containing:
                - "document_type": Set to "comparison"
                - "file_path": Full path to the merged document
                - "meta_tags": Meta tags from the merged document
                - "text": The merged full text
                - "source_file_paths": Full paths to the source documents
        """
        num_sentences = len(
            self._comparison_sentences[0]) if self._comparison_sentences else 0
        state = {"file_names": self._file_names,
                 "num_sentences": num_sentences,
                 "current_sentence_index": self._current_index,
                 "document_type": "comparison",
                 }
        if self._merged_document:
            state["file"] = self._merged_document.get_file_path(),
            state["meta_tags"] = self._merged_document.get_meta_tags()
            state["text"] = self._merged_document.get_text()
        if self._document_models:
            state["source_file_paths"] = [doc.get_file_path()
                                          for doc in self._document_models[1:]],
        return state

    def get_adoption_data(self, adoption_index: int) -> Dict[str, Union[List, IDocumentModel]]:
        """
        Prepares and removes the current sentence to be adopted into the merged document.

        This method retrieves the tag models for the selected annotator's version of the current
        sentence from the precomputed comparison_sentences_tags. 

        Args:
            adoption_index (int): The index of the annotator whose sentence should be adopted.

        Returns:
            Dict[str, Union[List, IDocumentModel]]: A dictionary containing:
                - "tag_models": The list of tag models to adopt.
                - "target_model": The merged document model to insert the tags into.
        """
        document_tags = self._document_models[adoption_index].get_tags()
        sentence = self._comparison_sentences[adoption_index][self._current_index]
        is_adopted = self._adopted_flags[self._current_index]

        return {
            "document_tags": document_tags,
            "sentence": sentence,
            "target_model": self._merged_document,
            "is_adopted": is_adopted
        }

    def get_sentence_offset(self) -> int:
        """
        Returns the character offset of the current raw sentence in the merged document text.

        The method uses the current index to retrieve the global sentence index from
        `self._differing_to_global`, then computes the total character offset by summing
        the lengths of all preceding sentences (including separators) in the merged text.

        Returns:
            int: Character offset of the sentence's start position in the merged document text.

        Raises:
            IndexError: If the current index is out of bounds for the offset list.
        """
        if self._current_index >= len(self._differing_to_global):
            raise IndexError(
                f"No global index available for current index {self._current_index}"
            )

        global_index = self._differing_to_global[self._current_index]

        merged_text = self._merged_document.get_text()
        sentences = merged_text.split("\n\n")
        separator_length = len("\n\n")

        offset = sum(len(sentences[i]) +
                     separator_length for i in range(global_index))
        return offset

    def get_raw_text_model(self) -> IDocumentModel:
        """
        Returns the document model containing the current raw (unannotated) sentence.

        This is the document model that holds the base sentence displayed in the comparison
        interface, typically shown in the first (leftmost) column.

        Returns:
            IDocumentModel: The document model holding the raw sentence.
        """
        return self._document_models[0]

    def get_text(self) -> str:
        """
        Returns the current text from the base document model.

        This method delegates to the first document in the list, which represents
        the raw unannotated version of the current sentence.

        Returns:
            str: The text of the document.
        """
        return self._document_models[0].get_text()

    def set_text(self, text: str) -> None:
        """
        Sets the text of the base document model.

        This method delegates the update to the first document in the list, which
        holds the raw unannotated sentence.

        Args:
            text (str): The new text to set.
        """
        self._document_models[0].set_text(text)

    def get_tags(self) -> List[ITagModel]:
        """
        Returns the list of tag models from the base document model.

        This method retrieves all tags associated with the raw sentence document.

        Returns:
            List[ITagModel]: A list of tag model instances.
        """
        return self._document_models[0].get_tags()

    def set_tags(self, tags: List[ITagModel]) -> None:
        """
        Sets the tag list for the base document model.

        This method delegates the tag update to the first document in the list.

        Args:
            tags (List[ITagModel]): The updated list of tag models.
        """
        self._document_models[0].set_tags(tags)

    def get_common_text(self) -> List[str]:
        """
        Returns the full list of raw sentences from the merged document.

        This is used to calculate global offsets and context for tag insertion.

        Returns:
            List[str]: A list of sentences from the merged document.
        """
        return self._merged_document.get_common_text()

    def set_meta_tags(self, meta_tags: Dict[str, List[ITagModel]]) -> None:
        """
        Sets meta tags for the base document model.

        This is typically used for metadata tags like document-level annotations.

        Args:
            meta_tags (Dict[str, List[ITagModel]]): A dictionary mapping tag types to tag model lists.
        """
        self._document_models[0].set_meta_tags(meta_tags)

    def get_file_path(self) -> str:
        """
        Returns the file path of the base document model.

        This method delegates to the first document in the list, which represents
        the raw unannotated version of the current sentence.

        Returns:
            str: The file path of the document.
        """
        return self._document_models[0].get_file_path()

    def set_file_path(self, file_path: str) -> None:
        """
        Sets the file path of the base document model.

        This method updates the file path in the first document of the list, which 
        represents the raw unannotated version of the current sentence.

        Args:
            file_path (str): The file path to assign to the document.
        """
        self._document_models[0].set_file_path(file_path)
