from typing import List
from model.annotation_document_model import AnnotationDocumentModel


class MergeDocumentModel(AnnotationDocumentModel):
    def __init__(self, document_data=None):
        super().__init__(document_data)
        self._separator = "\n\n"
        # if document_data:
        #     self._splitted_text = document_data["splitted_text"]
        #     self._text = self._separator.join(self._splitted_text)

    def get_splitted_text(self) -> List[str]:
        """
        Returns the splitted text as a list of sentences.

        Returns:
            List[str]: The list of sentences representing the splitted text.
        """
        return self._splitted_text

    def set_splitted_text(self, splitted_text: List[str]) -> None:
        """
        Sets the splitted text as a list of sentences.

        Args:
            splitted_text (List[str]): The list of sentences to be set as splitted text.
        """
        self._splitted_text = splitted_text
