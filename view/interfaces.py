from utils.interfaces import IDataObserver, ILayoutObserver


class IMetaTagsFrame(IDataObserver, ILayoutObserver):
    pass


class IComparisonHeaderFrame(IDataObserver, ILayoutObserver):
    pass


class IComparisonTextDisplays(IDataObserver, ILayoutObserver):
    pass


class ITextDisplayFrame(IDataObserver):
    pass


class IComparisonTextDisplayFrame(ITextDisplayFrame):
    pass
