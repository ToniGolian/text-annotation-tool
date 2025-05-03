from typing import List
from model.annotation_document_model import AnnotationDocumentModel


class MergeDocumentModel(AnnotationDocumentModel):
    def __init__(self, document_data=None):
        super().__init__(document_data)
        self._separator = "\n\n"

    def get_separator(self) -> str:
        """
        Returns the separator for text splitting.

        Returns:
            str: The separator for text splitting.
        """
        return self._separator

    def set_separator(self, separator: str) -> None:
        """
        Sets the separator for text splitting.

        Args:
            separator (str): The separator for text splitting.
        """
        self._separator = separator
