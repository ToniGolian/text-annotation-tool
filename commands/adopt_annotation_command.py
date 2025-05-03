from commands.interfaces import ICommand
from model.interfaces import IDocumentModel, ITagModel
from utils.tag_manager import TagManager
from typing import List


class AdoptAnnotationCommand(ICommand):
    """
    Command to adopt a list of tags into a document model using the TagManager.

    This command preserves UUIDs and equivalence information from the original tags,
    ensuring consistency when merging annotations across documents.

    Args:
        tag_manager (TagManager): Responsible for tag insertion and deletion.
        tag_models (List[ITagModel]): List of tags to be adopted into the document.
        target_model (IDocumentModel): The document model receiving the adopted tags.
    """

    def __init__(self, tag_manager: TagManager, tag_models: List[ITagModel], target_model: IDocumentModel):
        self._tag_manager = tag_manager
        self._tag_models = tag_models
        self._target_model = target_model
        self._inserted_uuids: List[str] = []
        self._executed = False

    def execute(self) -> None:
        """
        Executes the command by inserting all tags into the target model.
        """
        if self._executed:
            return
        print(f"DEBUG {len(self._tag_models)=}")
        for tag in self._tag_models:
            tag_data = tag.get_tag_data()
            uuid = self._tag_manager.add_tag(tag_data, self._target_model)
            self._inserted_uuids.append(uuid)
        self._executed = True

    def undo(self) -> None:
        """
        Removes all previously inserted tags from the target model.
        """
        for uuid in self._inserted_uuids:
            self._tag_manager.delete_tag(uuid, self._target_model)

    def redo(self) -> None:
        """
        Re-inserts the original tags into the target model.
        """
        self._inserted_uuids.clear()
        for tag in self._tag_models:
            tag_data = tag.get_tag_data()
            uuid = self._tag_manager.add_tag(tag_data, self._target_model)
            self._inserted_uuids.append(uuid)
