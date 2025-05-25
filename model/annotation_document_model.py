from typing import Dict, List, Tuple
from model.document_model import DocumentModel
from model.interfaces import IAnnotableDocumentModel, ITagModel
# from test_data.json.timex3_example_2 import doc


class AnnotationDocumentModel(DocumentModel, IAnnotableDocumentModel):
    """
    A specialized DocumentModel for managing annotation text.
    """

    def __init__(self, document_data: Dict = None):
        super().__init__(document_data)
        self._tags: List[ITagModel] = []
        # self._meta_tags: List[ITagModel] = []

    def get_tags(self) -> list:
        """
        Retrieves the tags associated with the document.

        Returns:
            list: A list of tags represented as ITagModel objects.
        """
        return self._tags

    def set_tags(self, tags: list) -> None:
        """
        Sets the tags associated with the document.

        Args:
            tags (list): A list of tags represented as ITagModel objects to set.
        """
        self._tags = tags
        self.notify_observers()

    # def get_meta_tags(self) -> list:
    #     """
    #     Retrieves the meta_tags associated with the document.

    #     Returns:
    #         list: A list of tags represented as ITagModel objects.
    #     """
    #     return self._meta_tags

    # def set_meta_tags(self, tags: list) -> None:
    #     """
    #     Sets the meta_tags associated with the document.

    #     Args:
    #         tags (list): A list of tags represented as ITagModel objects to set.
    #     """
    #     self._meta_tags = tags
    #     print(f" {self._meta_tags=}")
    #     self.notify_observers()

    def get_state(self) -> dict:
        """
        Retrieves a dictionary representation of the object's attributes.

        The dictionary includes the following attributes:
            - "document_type": The type of the document (e.g., "annotation", "comparison").
            - "file_path": The path, where the document is stored.
            - "file_name": The name of the file associated with the object.
            - "meta_tags": The metadata tags associated with the object.
            - "text": The textual content managed by the object.
            - "tags": The tags managed by the object.

        Returns:
            dict: A dictionary containing the object's attributes as keys and their corresponding values.
        """
        state = super().get_state()
        state.update({"tags": self._tags})
        return state
