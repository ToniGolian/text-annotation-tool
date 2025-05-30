from typing import Dict
from model.search_model import SearchModel


class SearchModels:
    """
    Manages a collection of SearchModel instances indexed by tag type.

    This class allows creation, retrieval, and validation management of search models
    associated with different tag types, and supports operations on individual or
    all stored models.
    """

    def __init__(self):
        """
        Initializes the search model database with an empty model registry.

        Internally, a dictionary is used to map tag type identifiers to SearchModel instances.
        """
        self._models: Dict[str, SearchModel] = {}

    def add_model(self, tag_type: str) -> None:
        """
        Creates and registers a new SearchModel for the specified tag type.

        If a model with the given tag type already exists, it will be replaced.

        Args:
            tag_type (str): The identifier used to associate the new SearchModel.
        """
        self._models[tag_type] = SearchModel()

    def has_model(self, tag_type: str) -> bool:
        """
        Checks whether a SearchModel is registered under the given tag type.

        Args:
            tag_type (str): The tag type to check.

        Returns:
            bool: True if a SearchModel exists for the given tag type, False otherwise.
        """
        return tag_type in self._models

    def has_valid_model(self, tag_type: str) -> bool:
        """
        Checks whether a valid and current SearchModel exists for the given tag type.

        This method returns False if either no model is registered under the given tag type,
        or the model exists but is marked as invalid.

        Args:
            tag_type (str): The tag type to check.

        Returns:
            bool: True if a valid and current SearchModel exists, False otherwise.
        """
        if tag_type not in self._models:
            return False
        return self._models[tag_type].is_valid()

    def get_search_model(self, tag_type: str) -> SearchModel:
        """
        Retrieves the SearchModel associated with a given tag type.

        Args:
            tag_type (str): The tag type whose SearchModel should be retrieved.

        Returns:
            SearchModel: The SearchModel registered under the given tag type.

        Raises:
            KeyError: If no model exists for the specified tag type.
        """
        return self._models[tag_type]

    def invalidate_model(self, tag_type: str) -> None:
        """
        Marks the SearchModel for a specific tag type as invalid.

        This should be used when the underlying data or configuration for that
        specific tag type changes.

        Args:
            tag_type (str): The tag type of the model to invalidate.

        Raises:
            KeyError: If no model exists for the specified tag type.
        """
        self._models[tag_type].invalidate()

    def invalidate_all(self) -> None:
        """
        Marks all registered SearchModel instances as invalid.

        This operation is useful when a global context change requires all models
        to be recalculated.
        """
        for model in self._models.values():
            model.invalidate()

    def clear_all(self) -> None:
        """
        Removes all SearchModel instances from the internal registry.

        After calling this method, the model dictionary will be empty.
        """
        self._models.clear()
