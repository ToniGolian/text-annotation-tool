from model.document_model import DocumentModel


class PreviewDocumentModel(DocumentModel):
    """
    A specialized DocumentModel for managing comparison text.
    """

    def __init__(self):
        super().__init__()
