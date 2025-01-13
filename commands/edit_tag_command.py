from typing import Dict
from commands.interfaces import ICommand
from utils.interfaces import ITagManager


class EditTagCommand(ICommand):
    """
    A command to change the data of an existing tag using the TagManager.
    Supports undo and redo functionality.
    """

    def __init__(self, tag_manager: ITagManager, tag_id: str, new_tag_data: Dict) -> None:
        """
        Initializes the ChangeTagCommand.

        Args:
            tag_manager (ITagManager): The tag manager responsible for managing tags.
            tag_id (str): The unique ID of the tag to be changed.
            new_tag_data (Dict): The new data to update the tag with.
        """
        self._tag_manager = tag_manager
        self._tag_id = tag_id
        self._new_tag_data = new_tag_data
        self._previous_tag_data = None  # Stores the original tag data for undo

    def execute(self) -> None:
        """
        Executes the command to change the tag's data.
        Stores the original data for undo functionality.
        """
        self._previous_tag_data = self._tag_manager.get_tag_data(self._tag_id)
        self._tag_manager.edit_tag(self._tag_id, self._new_tag_data)

    def undo(self) -> None:
        """
        Undoes the change by restoring the original tag data.
        """
        if self._previous_tag_data is not None:
            self._tag_manager.edit_tag(self._tag_id, self._previous_tag_data)

    def redo(self) -> None:
        """
        Redoes the change by applying the new tag data again.
        """
        if self._new_tag_data is not None:
            self._tag_manager.edit_tag(self._tag_id, self._new_tag_data)
