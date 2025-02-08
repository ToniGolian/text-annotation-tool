from commands.interfaces import ICommand
from model.interfaces import IDocumentModel
from utils.interfaces import ITagManager


class DeleteTagCommand(ICommand):
    """
    A command to remove a tag using the TagManager.
    Supports undo and redo functionality.
    """

    def __init__(self, tag_manager: ITagManager, tag_uuid: str, target_model: IDocumentModel) -> None:
        """
        Initializes the DeleteTagCommand.

        Args:
            tag_manager (ITagManager): The tag manager responsible for managing tags.
            tag_uuid (str): The unique ID of the tag to be removed.
            target_model (IDocumentModel): The document model where the tag is removed.
        """
        self._tag_manager = tag_manager
        self._target_model = target_model
        self._tag_uuid = tag_uuid
        self._tag_data = None  # Stores the tag's data for undo functionality

    def execute(self) -> None:
        """
        Executes the command to remove the tag from the document.

        Retrieves the tag's data before deletion to allow undo functionality.
        """
        self._tag_data = self._tag_manager.get_tag_data(
            self._tag_uuid, self._target_model)
        print(f"DEBUG delete command {self._tag_data=}")
        self._tag_manager.delete_tag(self._tag_uuid, self._target_model)

    def undo(self) -> None:
        """
        Reverts the deletion by restoring the tag with its original data.

        If the tag's data was stored, the tag is re-added to the document.
        """
        if self._tag_data is not None:
            self._tag_manager.add_tag(self._tag_data, self._target_model)

    def redo(self) -> None:
        """
        Re-executes the tag deletion.

        If the tag UUID is available, the tag is deleted again from the document.
        """
        if self._tag_uuid is not None:
            self._tag_manager.delete_tag(self._tag_uuid, self._target_model)
