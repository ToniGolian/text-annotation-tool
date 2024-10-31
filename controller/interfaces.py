from abc import ABC, abstractmethod
from commands.interfaces import ICommand
from model.interfaces import ITextModel, ITagModel

class IController(ABC):
    @abstractmethod
    def __init__(self, text_model: ITextModel, tag_model: ITagModel) -> None:
        """
        Initializes the controller with text and tag model dependencies.
        
        Args:
            text_model (ITextModel): The text model dependency.
            tag_model (ITagModel): The tag model dependency.
        """
        pass

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
