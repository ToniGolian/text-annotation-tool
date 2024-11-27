from typing import List, Dict
from abc import ABC, abstractmethod
from typing import Dict, List

from model.interfaces import ITagModel


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


class ITagManager(ABC):
    @abstractmethod
    def add_tag(self, tag_data: dict) -> None:
        """
        Simulates adding a tag by appending it to the tags list and updating the text.
        """

    @abstractmethod
    def edit_tag(self, tag_id: str, tag_data: dict) -> None:
        """
        Simulates editing a tag by updating the corresponding tag in the tags list.
        """
    @abstractmethod
    def delete_tag(self, tag_id: str) -> None:
        """
        Simulates deleting a tag by removing it from the tags list.
        """

    @abstractmethod
    def get_tag_data(self, tag_uuid: str) -> ITagModel:
        """
        Retrieves the data of a tag by its unique UUID.
        """


class ITagStringProcessor(ABC):
    """
    Interface for a processor that handles tag-to-string transformations
    and performs text operations involving tags.
    """

    @abstractmethod
    def tags_to_strings(self, tags: List[Dict]) -> List[str]:
        """
        Converts tag objects into their string representations.

        Args:
            tags (List[Dict]): A list of tag dictionaries.

        Returns:
            List[str]: A list of string representations of the tags.
        """
        pass

    @abstractmethod
    def insert_tag_into_text(self, text: str, tag_data: Dict) -> str:
        """
        Inserts a single tag as a string into the specified text.

        Args:
            text (str): The document text where the tag should be inserted.
            tag_data (Dict): A dictionary containing the tag data to insert.

        Returns:
            str: The updated text with the tag inserted at the specified position.
        """
        pass

    @abstractmethod
    def extract_tags_from_text(self, text: str) -> List[Dict]:
        """
        Extracts tag information from the text.

        Args:
            text (str): The document text.

        Returns:
            List[Dict]: A list of extracted tag dictionaries.
        """
        pass
