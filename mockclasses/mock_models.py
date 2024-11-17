from typing import Dict
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

    def get_data(self) -> Dict:
        """Retrieves the models data in a dictionary"""
        return {
            "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
            "document_title": "LoremIpsum"}


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

    def get_data(self) -> Dict:
        """Retrieves the models data in a dictionary"""
        return {"comparison_sentences": [["Plain Comparison Sentence", "Tagged Comparison <Tag> Sentence 01", "Tagged <Tag> Comparison Sentence 02"], ["2Plain Comparison Sentence", "2Tagged Comparison <Tag> Sentence 01", "2Tagged <Tag> Comparison Sentence 02"]],
                "file_names": ["File a", "File b", "File c", "File d"],
                "current_sentence_index": 1
                }


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

    def get_data(self) -> Dict:
        """Retrieves the models data in a dictionary"""
        return
