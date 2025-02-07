from commands.interfaces import ICommand
from model.interfaces import IDocumentModel
from utils.interfaces import ITagManager


class AddTagCommand(ICommand):
    def __init__(self, tag_manager: ITagManager, tag_data: dict, target_model: IDocumentModel) -> None:
        """
        Initializes the AddTagCommand with necessary dependencies.

        Args:
            tag_manager (ITagManager): The tag manager responsible for handling tag operations.
            tag_data (dict): The data for the tag to be added.
            target_model (IDocumentModel): The document model where the tag will be added.
        """
        self._tag_manager = tag_manager
        self._target_model = target_model
        self._tag_data = tag_data
        self._tag_uuid = None  # ID assigned by the TagManager

    def execute(self) -> None:
        """
        Executes the command to add a tag to the document.

        This method adds a new tag using the TagManager and stores its UUID 
        for potential undo operations.
        """
        print(f"DEBUG execute {self._tag_data=}")
        self._tag_uuid = self._tag_manager.add_tag(
            self._tag_data, self._target_model)

    def undo(self) -> None:
        """
        Reverts the addition of the tag.

        If a tag was successfully added, this method removes it using its stored UUID.
        """
        if self._tag_uuid is not None:
            self._tag_manager.delete_tag(self._tag_uuid, self._target_model)

    def redo(self) -> None:
        """
        Re-executes the tag addition after an undo.

        If tag data is available, the tag is re-added to the document.
        """
        print(f"DEBUG redo {self._tag_data=}")
        if self._tag_data is not None:
            self._tag_uuid = self._tag_manager.add_tag(
                self._tag_data, self._target_model)
