from abc import ABC, abstractmethod
from utils.interfaces import IObserver


class IMainFrame(ABC):
    @abstractmethod
    def render(self, parent):
        """Render the PDF extraction view in the specified parent frame."""
        pass


class IPDFExtractionView(ABC):
    @abstractmethod
    def render(self, parent):
        """Render the PDF extraction view in the specified parent frame."""
        pass


class ITextAnnotationView(ABC):
    @abstractmethod
    def render(self, parent):
        """Render the Text annotation view in the specified parent frame."""
        pass


class ITextComparisonView(ABC):
    @abstractmethod
    def render(self, parent):
        """Render the Text comparison view in the specified parent frame."""
        pass


class ITextDisplayFrame(IObserver):
    @abstractmethod
    def render(self, parent):
        """Render the text display frame in the specified parent frame."""
        pass


class ITaggingMenuFrame(IObserver):
    @abstractmethod
    def render(self, parent):
        """Render the tagging menu frame in the specified parent frame."""
        pass


class IComparisonDisplayFrame(IObserver):
    @abstractmethod
    def render(self, parent):
        """Render the display frame for annotation comparisons in the specified parent frame."""
        pass
