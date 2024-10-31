from abc import ABC, abstractmethod
from utils.interfaces import IObserver

class ITextModel(ABC):
    @abstractmethod
    def add_observer(self, observer: IObserver) -> None:
        """Adds an observer to be notified of changes."""
        pass

    @abstractmethod
    def remove_observer(self, observer: IObserver) -> None:
        """Removes an observer."""
        pass

    @abstractmethod
    def notify_observers(self) -> None:
        """Notifies all registered observers of changes."""
        pass

class ITagModel(ABC):
    pass