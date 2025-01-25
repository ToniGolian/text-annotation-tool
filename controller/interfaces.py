from abc import ABC, abstractmethod
from commands.interfaces import ICommand
from observer.interfaces import IDataObserver, ILayoutObserver, IObserver, IPublisher
from typing import List, Dict, Any


class IController(ABC):
    @abstractmethod
    def __init__(self, text_model: IPublisher) -> None:
        """
        Initializes the controller with text and tag model dependencies.

        Args:
            text_model (ITextModel): The text model dependency.
        """
        pass

    # command pattern
    @abstractmethod
    def _execute_command(self, command: ICommand) -> None:
        """Executes the specified command."""
        pass

    @abstractmethod
    def undo_command(self) -> None:
        """Reverses the last executed command."""
        pass

    @abstractmethod
    def redo_command(self) -> None:
        """Reapplies the last undone command."""
        pass

    # observer pattern
    @abstractmethod
    def add_observer(self, observer: IObserver, mapping_type: str) -> None:
        """Register observer to Model"""
        pass

    @abstractmethod
    def remove_observer(self, observer: IObserver, mapping_type: str) -> None:
        """Remove observer from Model"""
        pass

    @abstractmethod
    def get_observer_state(self, observer: IObserver, mapping_type: str) -> Any:
        """Retrieves the data from observed publisher."""
        pass

    # initializations

    @abstractmethod
    def finalize_views(self) -> None:
        """
        Finalizes the initialization of all views that were previously 
        not fully initialized.
        """
        pass

    # performances
    @abstractmethod
    def perform_text_selected(self, text: str) -> None:
        """Performs the action if a text is selected in the main text display."""
        pass

    @abstractmethod
    def perform_add_tag(self, tag_data: Dict, caller_id: str) -> None:
        """
        Abstract method to create and execute an AddTagCommand to add a new tag.

        Args:
            tag_data (Dict): A dictionary containing the data for the tag to be added.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        pass

    @abstractmethod
    def perform_edit_tag(self, tag_id: str, tag_data: Dict, caller_id: str) -> None:
        """
        Abstract method to create and execute an EditTagCommand to modify an existing tag.

        Args:
            tag_id (str): The unique identifier of the tag to be edited.
            tag_data (Dict): A dictionary containing the updated data for the tag.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        pass

    @abstractmethod
    def perform_delete_tag(self, tag_id: str, caller_id: str) -> None:
        """
        Abstract method to create and execute a DeleteTagCommand to remove a tag.

        Args:
            tag_id (str): The unique identifier of the tag to be deleted.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        pass
