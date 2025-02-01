from typing import List, Dict, Union
from abc import ABC, abstractmethod
from typing import Dict, List


class IObserver(ABC):
    @abstractmethod
    def update(self):
        """Called when data changes."""
        pass


class IPublisher(ABC):
    """
    A base interface for all publishers, managing both data and layout observers.
    """

    def __init__(self) -> None:
        """Initializes the publisher with empty lists for both data and layout observers."""
        self._observers: List[IObserver] = []

    def add_observer(self, observer: IObserver) -> None:
        """
        Adds an observer to the list if it is not already present.

        Args:
            observer (IObserver): The observer to be added.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        """
        Removes an observer from the list if it is present.

        Args:
            observer (IObserver): The observer to be removed.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self) -> None:
        """
        Notifies all registered observers of changes.
        Each observer should implement update() to handle the notification.
        """
        for observer in self._observers:
            observer.update(self)

    @abstractmethod
    def get_state(self) -> Dict[str, Union[str, int]]:
        """
        Retrieves the current state of the publisher.

        Returns:
            Dict: The state of the publisher.
        """
        pass
