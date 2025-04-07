from typing import List
from model.annotation_document_model import AnnotationDocumentModel


class MergeDocumentModel(AnnotationDocumentModel):
    def __init__(self, document_data=None):
        super().__init__(document_data)
        self._common_text = document_data["common_text"]
        self._separator = "\n\n"
        self._text = self._separator.join(self._common_text)

    def get_common_text(self) -> List[str]:
        """
        Returns the common text as a list of sentences.

        Returns:
            List[str]: The list of sentences representing the common text.
        """
        return self._common_text

    def set_common_text(self, common_text: List[str]) -> None:
        """
        Sets the common text as a list of sentences.

        Args:
            common_text (List[str]): The list of sentences to be set as common text.
        """
        self._common_text = common_text
