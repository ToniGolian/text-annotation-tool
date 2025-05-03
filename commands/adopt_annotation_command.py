from commands.interfaces import ICommand
from model.interfaces import IDocumentModel, ITagModel
from utils.tag_manager import TagManager
from typing import List


class AdoptAnnotationCommand(ICommand):
    """
    Command to adopt a list of tags into a document model using the TagManager.

    Ensures that all tags are inserted, tracked, and can be reverted or reapplied.

    Args:
        tag_manager (TagManager): Responsible for handling tag insertions and deletions.
        tag_models (List[ITagModel]): The list of tags to insert.
        target_model (IDocumentModel): The document model where tags are inserted.
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
        Prevents double execution to maintain a consistent state.
        """
        if self._executed:
            return
        for tag in self._tag_models:
            uuid = self._tag_manager.add_tag_from_model(
                tag, self._target_model)
            self._inserted_uuids.append(uuid)
        self._executed = True

    def undo(self) -> None:
        """
        Undoes the command by removing all inserted tags from the target model.
        """
        for uuid in self._inserted_uuids:
            self._tag_manager.delete_tag(uuid, self._target_model)

    def redo(self) -> None:
        """
        Redoes the command by re-inserting the same tags into the target model.
        Uses the original tag objects, assuming UUIDs and positions are preserved.
        """
        self._inserted_uuids.clear()
        for tag in self._tag_models:
            uuid = self._tag_manager.add_tag_from_model(
                tag, self._target_model)
            self._inserted_uuids.append(uuid)
