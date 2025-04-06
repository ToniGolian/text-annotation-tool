from model.annotation_document_model import AnnotationDocumentModel


class MergeDocumentModel(AnnotationDocumentModel):
    def __init__(self, document_data=None):
        super().__init__(document_data)
        self._common_text = document_data["common_text"]
        self._separator = "\n\n"
        self._text = self._separator.join(self._common_text)
