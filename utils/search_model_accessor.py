from model.search_model import SearchModel
from model.search_models import SearchModels
from utils.search_manager import SearchManager


class SearchModelAccessor:
    """
    Provides validated access to SearchModels via the DB and triggers updates if necessary.

    Combines model lookup with validation and automatic recalculation via SearchManager.
    """

    def __init__(self, search_models: SearchModels, manager: SearchManager):
        """
        Initializes the accessor with model registry and search computation backend.

        Args:
            search_models (SearchModels): The registry of search models by tag type.
            manager (SearchManager): Responsible for creating or updating search models.
        """
        self._search_models = search_models
        self._search_manager = manager

    def get_valid_model(self, tag_type: str) -> SearchModel:
        """
        Retrieves a valid SearchModel for the specified tag type.

        If no model exists or the existing model is invalid, a new model is
        calculated by the SearchManager before returning it from the registry.

        Args:
            tag_type (str): The tag type for which the SearchModel is requested.

        Returns:
            SearchModel: The up-to-date SearchModel associated with the tag type.
        """
        if not self._search_models.has_valid_model(tag_type):
            self._search_manager.calculate_model(tag_type)
        return self._search_models.get_search_model(tag_type)
