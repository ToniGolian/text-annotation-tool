from model.interfaces import ITextModel,ITagModel
from utils.interfaces import IObserver

class MockTextModel(ITextModel):
    def add_observer(self, observer: IObserver) -> None:
        """Adds an observer to be notified of changes."""
        pass

    def remove_observer(self, observer: IObserver) -> None:
        """Removes an observer."""
        pass

    def notify_observers(self) -> None:
        """Notifies all registered observers of changes."""
        pass

class MockTagModel(ITagModel):
    def add_observer(self, observer: IObserver) -> None:
        """Adds an observer to be notified of changes."""
        pass

    def remove_observer(self, observer: IObserver) -> None:
        """Removes an observer."""
        pass

    def notify_observers(self) -> None:
        """Notifies all registered observers of changes."""
        pass
