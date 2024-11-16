from abc import ABC, abstractmethod
from commands.interfaces import ICommand
from utils.interfaces import IObserver, IPublisher
from typing import List, Sequence


class IController(ABC):
    @abstractmethod
    def __init__(self, text_model: IPublisher, tag_model: IPublisher) -> None:
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
    def add_observer(self, observer: IObserver) -> None:
        """Register observer to Model"""
        pass

    @abstractmethod
    def remove_observer(self, observer: IObserver) -> None:
        """Remove observer from Model"""
        pass

    @abstractmethod
    def get_update_data(self, publisher: IPublisher):
        """Retrieves the data from observed publisher"""
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
