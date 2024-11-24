from abc import ABC, abstractmethod
from commands.interfaces import ICommand
from utils.interfaces import IDataObserver, ILayoutObserver, IObserver, IPublisher
from typing import List, Sequence


class IController(ABC):
    @abstractmethod
    def __init__(self, text_model: IPublisher, ) -> None:
        """
        Initializes the controller with text and tag model dependencies.

        Args:
            text_model (ITextModel): The text model dependency.
            tag_model (ITagModel): The tag model dependency.
        """
        pass

    # command pattern
    @abstractmethod
    def execute_command(self, command: ICommand) -> None:
        """Executes the specified command."""
        pass

    @abstractmethod
    def undo(self, command: ICommand) -> None:
        """Reverses the actions of the specified command."""
        pass

    @abstractmethod
    def redo(self, command: ICommand) -> None:
        """Reapplies the actions of the specified command."""
        pass

    # observer pattern
    @abstractmethod
    def add_data_observer(self, observer: IObserver, variables: List[str]) -> None:
        """Register observer to Model"""
        pass

    @abstractmethod
    def remove_data_observer(self, observer: IObserver) -> None:
        """Remove observer from Model"""
        pass

    @abstractmethod
    def add_layout_observer(self, observer: IObserver, variables: List[str]) -> None:
        """Register observer to Model"""
        pass

    @abstractmethod
    def remove_layout_observer(self, observer: IObserver) -> None:
        """Remove observer from Model"""
        pass

    @abstractmethod
    def get_data_state(self, observer: IDataObserver):
        """Retrieves the data from observed publisher"""
        pass

    @abstractmethod
    def get_layout_state(self, observer: ILayoutObserver):
        """Retrieves the layout data from observed publisher"""
        pass

    # initializiations
    @abstractmethod
    def finalize_views(self) -> None:
        """
        Finalizes the initialization of all views that were previously 
        not fully initialized."""
        pass

    # performances
    @abstractmethod
    def perform_text_selected(self, text: str) -> None:
        """Performs the action if a text is selected in the main text display"""
        pass

    @abstractmethod
    def perform_add_tag(self, tag_data: dict) -> None:
        """
        Perform the action of adding a new tag with the provided data.

        Args:
            tag_data (dict): The data of the tag to be added.
        """
        pass

    @abstractmethod
    def perform_edit_tag(self, tag_id: str, tag_data: dict) -> None:
        """
        Perform the action of editing an existing tag with the given ID and data.

        Args:
            tag_id (str): The ID of the tag to edit.
            tag_data (dict): The new data for the tag.
        """
        pass

    @abstractmethod
    def perform_delete_tag(self, tag_id: str) -> None:
        """
        Perform the action of deleting a tag with the given ID.

        Args:
            tag_id (str): The ID of the tag to delete.
        """
        pass
