from typing import Dict, List
from observer.interfaces import IPublisher, IObserver


class MockDocumentModel(IPublisher):
    def __init__(self) -> None:
        """Initializes the document model with an empty list of data observers."""
        self._data_observers: List[IObserver] = []

    def add_data_observer(self, observer: IObserver) -> None:
        """Adds a data observer to be notified of changes."""
        if observer not in self._data_observers:
            self._data_observers.append(observer)

    def remove_data_observer(self, observer: IObserver) -> None:
        """Removes a data observer."""
        if observer in self._data_observers:
            self._data_observers.remove(observer)

    def notify_observers(self) -> None:
        """Notifies all registered data observers of changes."""
        for observer in self._data_observers:
            observer.update(self)

    def get_state(self) -> Dict:
        """Retrieves the model's data in a dictionary."""
        return {
            "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
            "document_title": "LoremIpsum"
        }


class MockComparisonModel(IPublisher):
    def __init__(self) -> None:
        """Initializes the comparison model with separate observer lists for data and layout."""
        self._observers: List[IObserver] = []

    # Methods for Data Observers
    def add_observer(self, observer: IObserver) -> None:
        """Adds a data observer to be notified of changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        """Removes a data observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self) -> None:
        """Notifies all registered data observers of changes."""
        for observer in self._observers:
            observer.update(self)

    def get_state(self) -> Dict:
        """Retrieves the model's data in a dictionary."""
        return {
            "comparison_sentences": [
                ["Plain Comparison Sentence", "Tagged Comparison <Tag> Sentence 01",
                    "Tagged <Tag> Comparison Sentence 02"],
                ["2Plain Comparison Sentence", "2Tagged Comparison <Tag> Sentence 01",
                    "2Tagged <Tag> Comparison Sentence 02"]
            ],
            "file_names": ["File a", "File b", "File c", "File d"],
            "current_sentence_index": 1,
            "layout_type": "comparison",
            "current_page": 2,
            "total_pages": 5
        }


class MockTagModel:
    pass
