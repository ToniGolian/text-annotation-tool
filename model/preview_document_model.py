from model.document_model import DocumentModel
from observer.interfaces import IDataObserver


class PreviewDocumentModel(DocumentModel):
    """
    A specialized DocumentModel for managing preview text.
    """

    def __init__(self):
        super().__init__()

    def get_data_state(self):
        print(f"DEBUG get_data_state im PreviewDocumentModel")
        return super().get_data_state()
