from enums.search_types import SearchType
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

    def get_valid_model(self, search_str: str, search_type=SearchType.DB) -> SearchModel:
        """
        Retrieves a valid SearchModel for the specified search string.

        If no model exists or the current model is marked as invalid, a new one is
        calculated using the SearchManager based on the selected search type.

        The `search_type` indicates the mode of calculation (e.g., database-based or manual input),
        but does not affect retrieval. It is only relevant when a new model needs to be generated.

        Args:
            search_str (str): The identifier for which the SearchModel is requested.
            search_type (SearchType): The mode used to calculate the model if it is missing or invalid.

        Returns:
            SearchModel: The valid and up-to-date SearchModel associated with the given identifier.
        """
        if not self._search_models.has_valid_model(search_str):
            self._search_manager.calculate_model(search_str, search_type)
        return self._search_models.get_search_model(search_str)
