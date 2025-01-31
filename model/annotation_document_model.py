from typing import List, Tuple
from model.document_model import DocumentModel
from model.interfaces import ITagModel
from test_data.json.timex3_example_2 import doc


class AnnotationDocumentModel(DocumentModel):
    """
    A specialized DocumentModel for managing annotation text.
    """

    def __init__(self):
        super().__init__()
        self._tags: List[ITagModel] = []

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
