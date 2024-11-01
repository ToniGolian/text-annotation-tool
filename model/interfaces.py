from abc import ABC, abstractmethod
from utils.interfaces import IObserver


from abc import ABC, abstractmethod
from typing import List


class IModel(ABC):
    def __init__(self) -> None:
        """Initializes the model with an empty list of observers."""
        self._observers: List[IObserver] = []

    def add_observer(self, observer: IObserver) -> None:
        """
        Adds an observer to the observer list if it is not already present.

        Args:
            observer (IObserver): The observer to be added for notification.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        """
        Removes an observer from the observer list if it is present.

        Args:
            observer (IObserver): The observer to be removed from notification.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self) -> None:
        """
        Notifies all registered observers by calling their update method.
        Each observer in the list is notified of changes in the model.
        """
        for observer in self._observers:
            observer.update()


class IDocumentModel(IModel):
    pass


class ITagModel(IModel):
    pass
