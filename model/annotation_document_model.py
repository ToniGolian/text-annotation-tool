from model.document_model import DocumentModel


class AnnotationDocumentModel(DocumentModel):
    """
    A specialized DocumentModel for managing annotation text.
    """

    def __init__(self):
        super().__init__()
