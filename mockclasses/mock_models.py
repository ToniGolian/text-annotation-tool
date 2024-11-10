from utils.interfaces import IObserver, IPublisher
from model.interfaces import IComparisonModel, IDocumentModel


class MockDocumentModel(IDocumentModel):
    def add_observer(self, observer: IObserver) -> None:
        """Adds an observer to be notified of changes."""
        pass

    def remove_observer(self, observer: IObserver) -> None:
        """Removes an observer."""
        pass

    def notify_observers(self) -> None:
        """Notifies all registered observers of changes."""
        pass


class MockComparisonModel(IComparisonModel):
    def add_observer(self, observer: IObserver) -> None:
        """Adds an observer to be notified of changes."""
        pass

    def remove_observer(self, observer: IObserver) -> None:
        """Removes an observer."""
        pass

    def notify_observers(self) -> None:
        """Notifies all registered observers of changes."""
        pass


class MockTagModel(IPublisher):
    def add_observer(self, observer: IObserver) -> None:
        """Adds an observer to be notified of changes."""
        pass

    def remove_observer(self, observer: IObserver) -> None:
        """Removes an observer."""
        pass

    def notify_observers(self) -> None:
        """Notifies all registered observers of changes."""
        pass
