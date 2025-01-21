from commands.interfaces import ICommand
from utils.interfaces import ITagManager


class AddTagCommand(ICommand):
    def __init__(self, tag_manager: ITagManager, tag_data: dict) -> None:
        """
        Initializes the AddTagCommand.

        Args:
            tag_manager (ITagManager): The tag manager responsible for managing tags.
            tag_data (dict): The data for the tag to be added.
        """
        self._tag_manager = tag_manager
        self._tag_data = tag_data
        self._tag_uuid = None  # ID assigned by the TagManager

    def execute(self) -> None:
        """
        Executes the command to add a tag using the TagManager.
        Stores the ID of the newly added tag.
        """
        self._tag_uuid = self._tag_manager.add_tag(self._tag_data)

    def undo(self) -> None:
        """
        Undoes the addition of the tag by deleting it using its ID.
        """
        if self._tag_uuid is not None:
            self._tag_manager.delete_tag(self._tag_uuid)

    def redo(self) -> None:
        """
        Redoes the addition of the tag by re-adding it using the TagManager.
        """
        if self._tag_data is not None:
            self._tag_uuid = self._tag_manager.add_tag(self._tag_data)
