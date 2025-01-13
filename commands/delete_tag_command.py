from typing import Dict
from commands.interfaces import ICommand
from utils.interfaces import ITagManager


class DeleteTagCommand(ICommand):
    """
    A command to remove a tag using the TagManager.
    Supports undo and redo functionality.
    """

    def __init__(self, tag_manager: ITagManager, tag_id: str) -> None:
        """
        Initializes the RemoveTagCommand.

        Args:
            tag_manager (ITagManager): The tag manager responsible for managing tags.
            tag_id (str): The unique ID of the tag to be removed.
        """
        self._tag_manager = tag_manager
        self._tag_id = tag_id
        self._tag_data = None  # Stores the tag's data for undo functionality

    def execute(self) -> None:
        """
        Executes the command to remove the tag.
        Stores the tag's data for undo functionality.
        """
        self._tag_data = self._tag_manager.get_tag_data(self._tag_id)
        self._tag_manager.delete_tag(self._tag_id)

    def undo(self) -> None:
        """
        Undoes the removal by re-adding the tag with its original data.
        """
        if self._tag_data is not None:
            self._tag_manager.add_tag(self._tag_data)

    def redo(self) -> None:
        """
        Redoes the removal by deleting the tag again.
        """
        if self._tag_id is not None:
            self._tag_manager.delete_tag(self._tag_id)
