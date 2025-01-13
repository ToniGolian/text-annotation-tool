from model.document_model import DocumentModel


class PreviewDocumentModel(DocumentModel):
    """
    A specialized DocumentModel for managing preview text.
    """

    def __init__(self):
        super().__init__()
