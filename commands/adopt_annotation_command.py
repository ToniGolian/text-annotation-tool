from commands.interfaces import ICommand
from model.interfaces import IComparisonModel, IDocumentModel, ITagModel
from utils.tag_manager import TagManager
from typing import List, Dict


class AdoptAnnotationCommand(ICommand):
    """
    Command to adopt a list of tags into a document model using the TagManager.

    This command adjusts the positions of the adopted tags to fit the merged document
    and updates the differing_to_global mapping according to any changes in text length.
    It supports full undo and redo functionality, including offset tracking.

    Args:
        tag_manager (TagManager): Responsible for tag insertion and deletion.
        tag_models (List[ITagModel]): List of tags to be adopted.
        target_model (IDocumentModel): The document model receiving the tags.
        comparison_model (IComparisonModel): Provides sentence position context and offset mapping.
    """

    def __init__(
        self,
        tag_manager: TagManager,
        tag_models: List[ITagModel],
        target_model: IDocumentModel,
        comparison_model: IComparisonModel
    ):
        self._tag_manager = tag_manager
        self._tag_models = tag_models
        self._target_model = target_model
        self._comparison_model = comparison_model

        self._inserted_uuids: List[str] = []
        self._applied_offset: int = 0
        self._marked_sentence_index = 0
        self._executed = False

    def execute(self) -> None:
        """
        Inserts all tags into the target model, adjusts their positions to match
        the merged document, and updates the global offset mapping.
        """
        if self._executed:
            return

        sentence_offset = self._comparison_model.get_sentence_offset()
        # old_length = len(self._target_model.get_text())

        for tag in self._tag_models:
            tag_data = tag.get_tag_data()
            tag_data["position"] += sentence_offset
            uuid = self._tag_manager.add_tag(tag_data, self._target_model)
            self._inserted_uuids.append(uuid)

        self._marked_sentence_index = self._comparison_model.mark_current_sentence_as_adopted()
        self._executed = True

    def undo(self) -> None:
        """
        Removes the previously inserted tags and restores the original offset mapping.
        """
        for uuid in self._inserted_uuids:
            self._tag_manager.delete_tag(uuid, self._target_model)

        if self._applied_offset != 0:
            self._comparison_model._current_index = self._sentence_index
            self._comparison_model.adjust_differing_offsets(
                -self._applied_offset)

        self._executed = False
        self._inserted_uuids.clear()

    def redo(self) -> None:
        """
        Re-inserts the tags with correct positions and re-applies the offset mapping.
        """
        sentence_offset = self._comparison_model._differing_to_global[self._sentence_index]
        old_length = len(self._target_model.get_text())

        for tag in self._tag_models:
            tag_data = tag.get_tag_data()
            tag_data["position"] += sentence_offset
            uuid = self._tag_manager.add_tag(tag_data, self._target_model)
            self._inserted_uuids.append(uuid)

        new_length = len(self._target_model.get_text())
        offset = new_length - old_length

        # Redo must restore the same offset as originally applied
        assert offset == self._applied_offset, "Redo offset does not match original execution"

        if offset != 0:
            self._comparison_model._current_index = self._sentence_index
            self._comparison_model.adjust_differing_offsets(offset)

        self._executed = True
