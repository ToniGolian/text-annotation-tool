from abc import ABC, abstractmethod

class IObserver(ABC):
    @abstractmethod
    def update(self, data):
        """Updates the observer when notified by the publisher."""
        pass