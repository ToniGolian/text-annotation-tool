from abc import ABC, abstractmethod

class ICommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        """Executes the command's primary action."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Reverses the actions performed by execute."""
        pass

    @abstractmethod
    def redo(self) -> None:
        """Reapplies the actions undone by undo."""
        pass
