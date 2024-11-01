from typing import List, Dict
from model.interfaces import IDocumentModel
from controller.interfaces import IController
from model.interfaces import ITagModel


class DocumentModel(IDocumentModel):
    def __init__(self, controller: IController):
        self._controller = controller

        self._file_name: str = ""
        self._metatags: Dict = {}
        self._text: str = ""
        self._tags: List[ITagModel] = []

    # Getters and Setters

    def get_file_name(self) -> str:
        return self._file_name

    def set_file_name(self, file_name: str) -> None:
        self._file_name = file_name

    def get_metatags(self) -> dict:
        return self._metatags

    def set_metatags(self, metatags: dict) -> None:
        self._metatags = metatags

    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        self._text = text

    def get_tags(self) -> list:
        return self._tags

    def set_tags(self, tags: list) -> None:
        self._tags = tags
