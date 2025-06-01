from typing import Dict, Optional
from enums.search_types import SearchType
from model.search_model import SearchModel
from utils.search_manager import SearchManager


class SearchModelManager:
    """
    Central manager for search models.

    Ensures that only one model is active at a time, handles model lifecycle including
    validation and (re)calculation, and provides access to the currently activated model
    for behavioral control (e.g., next/previous navigation).
    """

    def __init__(self, search_manager: SearchManager):
        """
        Initializes the model manager with a computation backend.

        Args:
            search_manager (SearchManager): Component responsible for model calculation.
        """
        self._search_manager = search_manager
        self._models: Dict[str, SearchModel] = {}
        self._active_key: Optional[str] = None

    def get_active_model(self, tag_type: str, search_type: SearchType = SearchType.DB) -> SearchModel:
        """
        Retrieves and activates a valid SearchModel for the specified tag type.

        If the model does not exist or is invalid, it is recalculated.
        The requested model becomes the only active model; all others are deactivated.

        Args:
            tag_type (str): The tag type for which the model should be retrieved.
            search_type (SearchType): The calculation mode if recalculation is necessary.

        Returns:
            SearchModel: A valid, activated SearchModel instance.
        """
        # Recalculate if necessary
        model = self._models.get(tag_type)
        if model is None or not model.is_valid():
            model = self._search_manager.calculate_model(
                tag_type, search_type)
            self._models[tag_type] = model

        # Deactivate previous
        if self._active_key and self._active_key != tag_type:
            self._models[self._active_key].deactivate()

        # Activate current
        model.activate()
        self._active_key = tag_type
        model.next_result()

        return model

    def add_model(self, tag_type: str, model: SearchModel) -> None:
        """
        Registers a new SearchModel under the given tag type.

        This is typically called by the SearchManager after calculation.

        Args:
            tag_type (str): The tag type key.
            model (SearchModel): The model instance to register.
        """
        self._models[tag_type] = model

    def invalidate_all(self) -> None:
        """
        Marks all models as invalid, triggering recalculation on next access.
        """
        for model in self._models.values():
            model.invalidate()
