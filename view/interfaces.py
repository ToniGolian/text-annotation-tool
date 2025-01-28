from observer.interfaces import IDataObserver, ILayoutObserver


class IMetaTagsFrame(IDataObserver, ILayoutObserver):
    pass


class IComparisonHeaderFrame(IDataObserver, ILayoutObserver):
    pass


class IComparisonTextDisplays(IDataObserver, ILayoutObserver):
    pass


class IAnnotationMenuFrame(IDataObserver, ILayoutObserver):
    pass


class IExtractionFrame(IDataObserver):
    pass


class ITextDisplayFrame(IDataObserver):
    pass


class IComparisonTextDisplayFrame(ITextDisplayFrame):
    pass
