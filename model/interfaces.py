from utils.interfaces import IDataPublisher, ILayoutPublisher


class IComparisonModel(IDataPublisher, ILayoutPublisher):
    pass


class IConfigurationModel(ILayoutPublisher):
    pass


class ITagModel(IDataPublisher):
    pass


class IDocumentModel(IDataPublisher):
    pass
