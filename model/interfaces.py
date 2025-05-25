from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union
from observer.interfaces import IObserver, IPublisher, IPublisher


class ITagModel(ABC):
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


class IComparisonModel(IPublisher):
    """
    Interface for a comparison model that manages sentence-level differences between documents
    and provides mechanisms for annotation adoption and merged document construction.
    """

    def set_documents(self, documents: List[IDocumentModel]) -> None:
        """
        Sets the list of documents to be compared.

        Args:
            documents (List[IDocumentModel]): The list of annotated documents.
        """
        pass

    def register_comparison_displays(self, observers: List[IObserver]) -> None:
        """
        Registers observers for each document in the comparison display.

        Args:
            observers (List[IObserver]): The observers for each comparison document.
        """
        pass

    def set_comparison_data(self, comparison_data: Dict[str, Union[List[str], List[List[str]], List[int]]]) -> None:
        """
        Initializes the comparison model with sentence alignment data and global mapping.

        Args:
            comparison_data (Dict): A dictionary containing:
                - "comparison_sentences": List of sentence lists (first list is raw text).
                - "differing_to_global": List of global indices per differing sentence.
                - "merged_document": The output document model where adopted tags go.
        """
        pass

    def next_sentence(self) -> None:
        """
        Advances to the next differing sentence in the list, wrapping around if necessary.
        """
        pass

    def previous_sentence(self) -> None:
        """
        Moves to the previous differing sentence in the list, wrapping around if necessary.
        """
        pass

    def mark_current_sentence_as_adopted(self) -> int:
        """
        Marks the currently selected sentence as adopted and advances to the next unadopted one.

        Returns:
            int: The index of the adopted sentence in the differing list.
        """
        pass

    def get_adoption_data(self, adoption_index: int) -> Dict[str, Union[List[ITagModel], IDocumentModel, str, bool]]:
        """
        Retrieves the necessary data to adopt the current sentence from one of the annotators.

        Args:
            adoption_index (int): The annotator index from which to take tags.

        Returns:
            Dict: A dictionary with "document_tags", "sentence", "target_model", "is_adopted".
        """
        pass

    def get_sentence_offset(self) -> int:
        """
        Returns the character offset in the merged document where the current sentence begins.

        Returns:
            int: The character offset in the merged document.
        """
        pass

    def get_raw_text_model(self) -> IDocumentModel:
        """
        Returns the document model containing the current raw sentence.

        Returns:
            IDocumentModel: The source document with the untagged sentence.
        """
        pass

# class IComparisonModel:
#     """
#     Interface for a comparison model that manages document comparisons and iterates over
#     sentence pairs.

#     This model allows setting document-observer pairs, storing and navigating comparison
#     sentences, and updating document texts accordingly.
#     """

#     def set_documents(self, documents: List[IDocumentModel]) -> None:
#         """
#         Sets the list of documents and updates the file names.

#         This method updates the internal document list and ensures that the file names
#         are stored accordingly. It also notifies observers about the changes.

#         Args:
#             documents (List[IDocumentModel]): The list of document models.
#         """
#         pass

#     def register_comparison_displays(self, observers: List[IObserver]) -> None:
#         """
#         Registers observers for the documents.

#         This method assigns an observer to each document to track updates and changes.
#         The number of documents and observers must match.

#         Args:
#             observers (List[IObserver]): The list of observers.

#         Raises:
#             ValueError: If the number of documents and observers does not match.
#         """
#         pass

#     def set_comparison_data(self, comparison_data: Dict[str, Union[str, List[Tuple[str, ...]]]]) -> None:
#         """
#         Sets the comparison data including common text and sentence comparisons.

#         Args:
#             comparison_data (Dict[str, Union[str, List[Tuple[str, ...]]]]]):
#                 A dictionary containing:
#                 - "common_text" (str): The shared text across comparisons.
#                 - "comparison_sentences" (List[Tuple[str, ...]]): A list of sentence tuples,
#                 where each tuple contains a variable number of strings.
#         """
#         pass

#     def next_sentence(self) -> None:
#         """
#         Advances to the next sentence tuple in the comparison sentences list.
#         If at the last element, it wraps around to the first element.
#         """
#         pass

#     def previous_sentence(self) -> None:
#         """
#         Moves to the previous sentence tuple in the comparison sentences list.
#         If at the first element, it wraps around to the last element.
#         """
#         pass

#     def remove_current_sentence(self) -> None:
#         """
#         Removes the currently selected sentence tuple from the comparison sentences list.
#         After removal, it moves to the next available sentence.
#         If the last element is removed, it wraps around to the first element.
#         If the list becomes empty, no further action is taken.
#         """
#         pass


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
