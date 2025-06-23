from typing import Dict, Optional, Tuple
from enums.search_types import SearchType
from model.interfaces import IDocumentModel
from model.search_model import SearchModel
from observer.interfaces import IPublisher
from utils.search_manager import SearchManager


class SearchModelManager(IPublisher):
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
        super().__init__()
        self._search_manager = search_manager
        self._manual_models: Dict[str, SearchModel] = {}
        self._db_models: Dict[str, SearchModel] = {}
        self._active_key: Optional[str] = None
        self._current_search_config = None

    def get_active_model(self, tag_type: str = None, search_type: SearchType = SearchType.DB, document_model: IDocumentModel = None, options: Optional[Dict] = None) -> SearchModel:
        """
        Retrieves and activates a valid SearchModel for the specified search context.

        This method manages both database-based and manual search models:
        - For DB search: it retrieves or recalculates a model based on the tag type.
        - For manual search: it uses the search term as the key and builds the model
          based on custom options (e.g., case sensitivity, regex).

        If the model does not exist or is invalid, it will be recalculated.
        Only one model is active at a time; previously active models are deactivated.

        Args:
            tag_type (str, optional): The tag type identifier (used only for DB search).
            search_type (SearchType): The search strategy (DB or MANUAL).
            document_model (IDocumentModel, optional): The source document to search in.
            options (Dict, optional): Parameters for manual search (keys: 'search_term', 'case_sensitive', 'whole_word', 'regex').

        Returns:
            SearchModel: A valid, activated SearchModel instance.
        """
        # Store the current search configuration to restore later if needed
        self._current_search_config = {
            "tag_type": tag_type,
            "search_type": search_type,
            "document_model": document_model,
            "options": options,
        }

        if search_type == SearchType.MANUAL:
            search_term = options.get("search_term", "")
            model = self._manual_models.get(search_term)
            if model is None or not model.is_valid():
                model = self._search_manager.calculate_manual_search_model(
                    options=options, document_model=document_model)
                self._register_observers_to_search_model(model)
                self._manual_models[search_term] = model
            key = search_term  # for activation tracking

        elif search_type == SearchType.DB:
            model = self._db_models.get(tag_type)
            if model is None or not model.is_valid():
                model = self._search_manager.calculate_db_search_model(
                    tag_type=tag_type, document_model=document_model)
                self._register_observers_to_search_model(model)
                self._db_models[tag_type] = model
            key = tag_type  # for activation tracking

        # Deactivate previous model if different
        if self._active_key and self._active_key != key:
            # Deactivate the old model from either dict
            old_model = (
                self._manual_models.get(self._active_key)
                or self._db_models.get(self._active_key)
            )
            if old_model:
                old_model.deactivate()

        # Activate current
        model.activate()
        self._active_key = key

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
        for model in self._manual_models.values():
            model.invalidate()
        for model in self._db_models.values():
            model.invalidate()

    def deactivate_active_search_model(self) -> None:
        """
        Deactivates the currently active model, if one is set.
        """
        if self._active_key:
            self._manual_models[self._active_key].deactivate()
            self._db_models[self._active_key].deactivate()
            self._active_key = None

    def deactivate_active_manual_search_model(self) -> None:
        """
        Deactivates the currently active manual search model, if one is set.
        """
        if self._active_key and self._active_key in self._manual_models:
            self._manual_models[self._active_key].deactivate()
            self._active_key = None

    def _register_observers_to_search_model(self, model: SearchModel) -> None:
        """
        Registers all current observers to a new SearchModel instance.

        This is used when a new model is created or recalculated.
        Args:
            model (SearchModel): The model instance to which observers should be added.
        """
        for observer in self._observers:
            model.add_observer(observer)

    def get_state(self):
        """Just to use the class as proxy for the observer interface."""
        return super().get_state()

    def reset_models(self) -> None:
        """
        Resets all models, clearing the internal dictionaries and deactivating any active model.
        """
        self._manual_models.clear()
        for model in self._db_models.values():
            model.reset()
        self._active_key = None
        self.notify_observers()

    def update_model(self, model: SearchModel) -> SearchModel:
        """
        Recomputes the active model using the stored configuration and restores its current index.

        Args:
            model (SearchModel): The model whose index state should be preserved.

        Returns:
            SearchModel: The updated model with restored index.
        """
        if not model:
            return None
        current_index = model.get_current_index()
        config = self._current_search_config

        updated_model = self.get_active_model(
            tag_type=config["tag_type"],
            search_type=config["search_type"],
            document_model=config["document_model"],
            options=config["options"],
        )

        updated_model.set_current_index(current_index)
        return updated_model
