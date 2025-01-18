from typing import List, Dict
from abc import ABC, abstractmethod
from typing import Dict, List


class IObserver(ABC):
    pass


class IDataObserver(IObserver):
    @abstractmethod
    def update_data(self):
        """Called when data changes."""
        pass


class ILayoutObserver(IObserver):

    @abstractmethod
    def update_layout(self):
        """Called when layout changes."""
        pass


class IPublisher(ABC):
    """
    A base interface for all publishers.
    """
    pass


class IDataPublisher(IPublisher):
    """
    A specialized interface for publishers managing data observers.
    """

    def __init__(self) -> None:
        """Initializes the data publisher with an empty list of data observers."""
        self._data_observers: List[IDataObserver] = []

    def add_data_observer(self, observer: IDataObserver) -> None:
        """
        Adds a data observer to the list if it is not already present.

        Args:
            observer (IDataObserver): The data observer to be added.
        """
        if observer not in self._data_observers:
            self._data_observers.append(observer)

    def remove_data_observer(self, observer: IDataObserver) -> None:
        """
        Removes a data observer from the list if it is present.

        Args:
            observer (IDataObserver): The data observer to be removed.
        """
        if observer in self._data_observers:
            self._data_observers.remove(observer)

    def notify_data_observers(self) -> None:
        """
        Notifies all registered data observers of data changes.
        """
        for observer in self._data_observers:
            observer.update_data()

    @abstractmethod
    def get_data_state(self) -> Dict:
        """Retrieves the data state of the publisher."""
        pass


class ILayoutPublisher(IPublisher):
    """
    A specialized interface for publishers managing layout observers.
    """

    def __init__(self) -> None:
        """Initializes the layout publisher with an empty list of layout observers."""
        self._layout_observers: List[ILayoutObserver] = []

    def add_layout_observer(self, observer: ILayoutObserver) -> None:
        """
        Adds a layout observer to the list if it is not already present.

        Args:
            observer (ILayoutObserver): The layout observer to be added.
        """
        if observer not in self._layout_observers:
            self._layout_observers.append(observer)

    def remove_layout_observer(self, observer: ILayoutObserver) -> None:
        """
        Removes a layout observer from the list if it is present.

        Args:
            observer (ILayoutObserver): The layout observer to be removed.
        """
        if observer in self._layout_observers:
            self._layout_observers.remove(observer)

    def notify_layout_observers(self) -> None:
        """
        Notifies all registered layout observers of layout changes.
        """
        for observer in self._layout_observers:
            observer.update_layout()

    @abstractmethod
    def get_layout_state(self) -> Dict:
        """Retrieves the layout state of the publisher."""
        pass
