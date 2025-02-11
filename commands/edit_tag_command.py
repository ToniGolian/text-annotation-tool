from typing import Dict
from commands.interfaces import ICommand
from model.interfaces import IDocumentModel
from utils.interfaces import ITagManager


class EditTagCommand(ICommand):
    """
    A command to modify the data of an existing tag using the TagManager.
    Supports undo and redo functionality.
    """

    def __init__(self, tag_manager: ITagManager, tag_uuid: str, new_tag_data: Dict, target_model: IDocumentModel) -> None:
        """
        Initializes the EditTagCommand.

        Args:
            tag_manager (ITagManager): The tag manager responsible for managing tags.
            tag_uuid (str): The unique ID of the tag to be modified.
            new_tag_data (Dict): The updated data for the tag.
            target_model (IDocumentModel): The document model where the tag exists.
        """
        self._tag_manager = tag_manager
        self._target_model = target_model
        self._tag_uuid = tag_uuid
        self._previous_tag_data = self._tag_manager.get_tag_data(
            self._tag_uuid, self._target_model)  # Stores the original tag data for undo

        new_attributes = new_tag_data["attributes"]
        new_attributes["id"] = self._previous_tag_data["attributes"]["id"]
        self._new_tag_data = {**self._previous_tag_data,
                              "attributes": new_attributes}

    def execute(self) -> None:
        """
        Executes the command to modify the tag's data.

        Stores the original tag data before applying the modifications.
        """
        self._tag_manager.edit_tag(
            self._tag_uuid, self._new_tag_data, self._target_model)

    def undo(self) -> None:
        """
        Reverts the modification by restoring the original tag data.

        If the original tag data was stored, it is reapplied to the tag.
        """
        if self._previous_tag_data is not None:
            self._tag_manager.edit_tag(
                self._tag_uuid, self._previous_tag_data, self._target_model)

    def redo(self) -> None:
        """
        Reapplies the modification by updating the tag with the new data again.

        If the new tag data is available, it is applied once more.
        """
        if self._new_tag_data is not None:
            self._tag_manager.edit_tag(
                self._tag_uuid, self._new_tag_data, self._target_model)
