from typing import List, Dict
from model.interfaces import IDocumentModel
from model.interfaces import ITagModel


class DocumentModel(IDocumentModel):
    def __init__(self):
        self._filename: str = ""
        self._meta_tags: Dict = {}
        self._text: str = ""
        self._tags: List[ITagModel] = []

    # Getters and Setters

    def get_filename(self) -> str:
        return self._filename

    def set_filename(self, file_name: str) -> None:
        self._filename = file_name

    def get_meta_tags(self) -> dict:
        return self._meta_tags

    def set_meta_tags(self, metatags: dict) -> None:
        self._meta_tags = metatags

    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        self._text = text

    def get_tags(self) -> list:
        return self._tags

    def set_tags(self, tags: list) -> None:
        self._tags = tags
