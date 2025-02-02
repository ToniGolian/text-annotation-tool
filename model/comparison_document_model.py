from model.document_model import DocumentModel
from model.interfaces import IAnnotableDocumentModel


class ComparisonDocumentModel(DocumentModel, IAnnotableDocumentModel):
    """
    A specialized DocumentModel for managing comparison text.
    """

    def __init__(self):
        super().__init__()

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
