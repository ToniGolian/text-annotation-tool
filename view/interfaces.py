from abc import ABC
from observer.interfaces import IObserver


class IView(ABC):
    pass


class IMetaTagsFrame(IObserver):
    pass


class IComparisonHeaderFrame(IObserver):
    pass


class IComparisonTextDisplays(IObserver):
    pass


class IAnnotationMenuFrame(IObserver):
    pass


class IExtractionFrame(IObserver):
    pass


class ITextDisplayFrame(IObserver):
    pass


# class IComparisonTextDisplayFrame(ITextDisplayFrame):
#     pass


class IComparisonView(ITextDisplayFrame):
    pass
