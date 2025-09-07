from commands.add_tag_command import AddTagCommand
from commands.adopt_annotation_command import AdoptAnnotationCommand
from commands.delete_tag_command import DeleteTagCommand
from commands.edit_tag_command import EditTagCommand
from enums.failure_reasons import FailureReason
from controller.interfaces import IController
from commands.interfaces import ICommand
from enums.menu_pages import MenuPage
from enums.wizard_types import ProjectWizardType, TagWizardType
from enums.search_types import SearchType
from input_output.file_handler import FileHandler
from model.annotation_document_model import AnnotationDocumentModel
from model.global_settings_model import GlobalSettingsModel
from model.highlight_model import HighlightModel
from model.interfaces import IComparisonModel, ILayoutConfigurationModel, IDocumentModel, ISearchModel, ISelectionModel
from model.project_settings_model import ProjectSettingsModel
from model.project_wizard_model import ProjectWizardModel
from model.save_state_model import SaveStateModel
from model.tag_model import TagModel
from model.undo_redo_model import UndoRedoModel
from observer.interfaces import IPublisher, IObserver, IPublisher, IObserver
from typing import Any, Callable, Dict, List,  Tuple
from utils.color_manager import ColorManager
from utils.comparison_manager import ComparisonManager
from utils.project_configuration_manager import ProjectConfigurationManager
from utils.path_manager import PathManager
from utils.pdf_extraction_manager import PDFExtractionManager
from utils.project_directory_manager import ProjectDirectoryManager
from utils.search_manager import SearchManager
from utils.search_model_manager import SearchModelManager
from utils.settings_manager import SettingsManager
from utils.suggestion_manager import SuggestionManager
from utils.tag_manager import TagManager
from utils.tag_processor import TagProcessor
from view.interfaces import IComparisonView, IView
import tkinter.messagebox as mbox

from view.main_window import MainWindow


class Controller(IController):
    def __init__(self, layout_configuration_model: ILayoutConfigurationModel, preview_document_model: IPublisher = None, annotation_document_model: IPublisher = None, comparison_model: IComparisonModel = None, selection_model: IPublisher = None,  highlight_model: IPublisher = None, annotation_mode_model: IPublisher = None, save_state_model: IPublisher = None, project_wizard_model: IPublisher = None, global_settings_model: IPublisher = None, project_settings_model: IPublisher = None) -> None:

        # state
        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observer_layout_map: Dict[IObserver, Dict] = {}

        self._layout_configuration_model: IPublisher = layout_configuration_model
        self._project_wizard_model: ProjectWizardModel = project_wizard_model
        self._global_settings_model: GlobalSettingsModel = global_settings_model
        self._project_settings_model: ProjectSettingsModel = project_settings_model

        self._extraction_document_model: IDocumentModel = preview_document_model
        self._annotation_document_model: IDocumentModel = annotation_document_model
        self._comparison_model: IComparisonModel = comparison_model
        self._selection_model: ISelectionModel = selection_model
        self._annotation_mode_model: IPublisher = annotation_mode_model
        self._highlight_model = highlight_model
        self._current_search_model: IPublisher = None
        self._save_state_model: SaveStateModel = save_state_model

        # dependencies
        self._path_manager = PathManager()
        self._file_handler = FileHandler(path_manager=self._path_manager)
        self._project_directory_manager = ProjectDirectoryManager(
            self._file_handler)
        self._project_configuration_manager = ProjectConfigurationManager(
            self._file_handler)
        self._suggestion_manager = SuggestionManager(self, self._file_handler)
        self._settings_manager = SettingsManager(self._file_handler)
        self._tag_processor = TagProcessor(self)
        self._tag_manager = TagManager(self, self._tag_processor)
        self._comparison_manager = ComparisonManager(self, self._tag_processor)
        self._pdf_extraction_manager = PDFExtractionManager(controller=self)

        self._search_manager = SearchManager(file_handler=self._file_handler)
        self._search_model_manager = SearchModelManager(self._search_manager)
        self._color_manager = ColorManager(self._file_handler)

        # config
        self.update_project_name()
        # Load the source mapping once and store it in an instance variable
        self._source_mapping = self._file_handler.read_file(
            "source_mapping")

        # views
        self._main_window: MainWindow = None
        self._comparison_view: IComparisonView = None
        self._views_to_finalize: List = []
        self._search_views: List = []

        # command pattern
        self._active_view_id = None  # Track the currently active view
        self._undo_redo_models: Dict[str, UndoRedoModel] = {}

        # maps view ids to document sources for save actions
        self._document_source_mapping = {"extraction": self._extraction_document_model,
                                         "annotation": self._annotation_document_model,
                                         "comparison": self._comparison_model}

    # decorators
    def invalidate_search_models(method):
        """
        Decorator to invalidate all search models before executing a method.
        """

        def wrapper(self, *args, **kwargs):
            self._search_model_manager.invalidate_all()
            return method(self, *args, **kwargs)
        return wrapper

    def update_current_search_model(method):
        """
        Decorator to update the current search model after method execution.
        If the calling method is perform_add_tag, the search pointer moves to the next result.
        """

        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            if not self._current_search_model:
                return result
            self._current_search_model = self._search_model_manager.update_model(
                self._current_search_model)
            if method.__name__ == "perform_add_tag":
                self.perform_next_suggestion()
            return result
        return wrapper

    def with_highlight_update(method):
        """
        Decorator that ensures the highlight model is updated after the decorated method is executed.

        This is useful for controller methods that modify search or tag data which affects highlighting.

        Args:
            method (Callable): The method to wrap.

        Returns:
            Callable: The wrapped method that updates the highlight model after execution.
        """

        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._update_highlight_model()
            return result
        return wrapper

    def reset_search(method):
        """
        Decorator to reset all search-related states before executing a method.
        This includes switching to manual mode, resetting all search models,
        and clearing the current active search model.
        """

        def wrapper(self, *args, **kwargs):
            self._annotation_mode_model.set_manual_mode()
            self._search_model_manager.reset_models()
            self._current_search_model = None
            for search_view in self._search_views:
                search_view.reset_entry()
            return method(self, *args, **kwargs)
        return wrapper

    def track_save_state(method):
        """
        Decorator that adjusts the SaveStateModel based on the type of command action.

        This decorator should be applied to controller methods that manage commands,
        such as execute, undo, and redo. It automatically updates the change counter
        for the active view in the SaveStateModel:

        - Calls to 'execute' and 'redo' will increment the counter (marking the view dirty).
        - Calls to 'undo' will decrement the counter (potentially marking it clean again).

        Needs to be the most inner decorator to ensure it wraps around the command execution logic.

        """

        def wrapped(self, *args, **kwargs):
            result = method(self, *args, **kwargs)

            name = method.__name__.lower()
            key = self._active_view_id
            if "undo" in name:
                self._save_state_model.decrement(key)
            elif "_execute" in name or "redo" in name:
                self._save_state_model.increment(key)

            return result

        return wrapped

    def check_for_saving_before(method):
        """
        Decorator that ensures unsaved changes are handled before executing the decorated method.

        Calls `self.check_for_saving()` to prompt the user for saving any dirty views
        before proceeding with the decorated operation.

        """

        def wrapped(self, *args, **kwargs):
            self.check_for_saving()
            return method(self, *args, **kwargs)

        return wrapped

    def reset_project_relevant_models(method):
        """
        Decorator that resets the project-related models after executing a method.

        Args:
            method (Callable): The method to wrap.

        Returns:
            Callable: The wrapped method that resets the save state after execution.
        """

        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._extraction_document_model.reset()
            self._annotation_document_model.reset()
            self._comparison_model.reset()
            self._selection_model.reset()
            self._annotation_mode_model.reset()
            self._highlight_model.reset()
            self._save_state_model.reset()
            self._current_search_model = None
            return result
        return wrapper

    # command pattern

    @with_highlight_update
    @invalidate_search_models
    @update_current_search_model
    @track_save_state  # ! needs to be the most inner decorator!
    def _execute_command(self, command: ICommand, caller_id: str) -> None:
        """
        Executes a command, adds it to the undo stack of the corresponding view,
        and clears the redo stack for that view.

        Args:
            command (ICommand): The command object to execute.
            caller_id (str): The unique identifier for the view initiating the command.
        """
        if caller_id in self._undo_redo_models:

            model = self._undo_redo_models[caller_id]
            model.execute_command(command)
            command.execute()

    @with_highlight_update
    @invalidate_search_models
    @update_current_search_model
    @track_save_state
    def undo_command(self, caller_id: str = None) -> None:
        """
        Undoes the last command for the specified or active view by moving it from the undo stack
        to the redo stack and calling its undo method.

        Args:
            caller_id (str, optional): The unique identifier for the view requesting the undo.
                                       Defaults to the currently active view.
        """
        if not caller_id:
            caller_id = self._active_view_id
        if caller_id in self._undo_redo_models:
            model = self._undo_redo_models[caller_id]
            command = model.undo_command()
            if command:
                command.undo()

    @with_highlight_update
    @invalidate_search_models
    @update_current_search_model
    @track_save_state
    def redo_command(self, caller_id: str = None) -> None:
        """
        Redoes the last undone command for the specified or active view by moving it from the redo stack
        to the undo stack and calling its redo method.

        Args:
            caller_id (str, optional): The unique identifier for the view requesting the redo.
                                       Defaults to the currently active view.
        """
        if not caller_id:
            caller_id = self._active_view_id
        if caller_id in self._undo_redo_models:
            model = self._undo_redo_models[caller_id]
            command = model.redo_command()
            if command:
                command.redo()

    # observer pattern

    def add_observer(self, observer: IObserver) -> None:
        """
        Registers an observer to all relevant publishers based on the predefined mapping.

        This method retrieves all publishers related to the observer and registers it
        dynamically by checking the keys in `source_keys`.

        Args:
            observer (IObserver): The observer to be added.

        Raises:
            KeyError: If no mapping exists for the given observer.
        """
        # Retrieve the full mapping for the observer (without specifying a publisher)
        observer_config = self._get_observer_config(observer)

        # Iterate through all publishers by extracting keys from `source_keys`
        for config in observer_config.values():
            finalize = config["finalize"]
            source_keys = config["source_keys"]

            # Extract publisher instances dynamically based on `source_keys`
            for publisher_key in source_keys.keys():
                # Convert the string key into the actual instance stored in the Controller
                publisher_instance = getattr(self, f"_{publisher_key}", None)

                if publisher_instance is None:
                    print(
                        f"INFO: Publisher '{publisher_key}' not yet available for observer '{observer.__class__.__name__}'")
                else:  # Register observer with the publisher
                    publisher_instance.add_observer(observer)

            # Add observer to finalize list if required
            if finalize and observer not in self._views_to_finalize:
                self._views_to_finalize.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        """
        Removes an observer from all relevant publishers and clears any associated mappings or registrations.

        This method dynamically retrieves all publishers related to the observer and removes the observer
        from them by resolving the publisher names via Controller attributes.

        Args:
            observer (IObserver): The observer to be removed.

        Raises:
            KeyError: If no mapping exists for the given observer or a publisher instance cannot be resolved.
        """
        # Retrieve the full mapping for the observer (without specifying a publisher)
        observer_config = self._get_observer_config(observer)

        # Iterate through all publishers by extracting keys from `source_keys`
        for config in observer_config.values():
            source_keys = config["source_keys"]

            for publisher_key in source_keys.keys():
                # Convert the string key into the actual instance stored in the Controller
                publisher_instance = getattr(self, f"_{publisher_key}", None)

                if publisher_instance is None:
                    continue

                # Remove observer from the publisher
                publisher_instance.remove_observer(observer)

        # If the observer was added to the finalize list, remove it
        if observer in self._views_to_finalize:
            self._views_to_finalize.remove(observer)
        if observer in self._search_views:
            self._search_views.remove(observer)

    def get_observer_state(self, observer: IObserver, publisher: IPublisher = None) -> dict:
        """
        Retrieves the updated state information for a specific observer and publisher.

        If a required data source (publisher) is not yet available, it is ignored temporarily,
        but the subscription remains valid and will be re-evaluated on the next update.

        Args:
            observer (IObserver): The observer requesting updated state information.
            publisher (IPublisher, optional): The publisher that triggered the update. Defaults to None.

        Returns:
            dict: The computed state information specific to the requesting observer.

        Raises:
            KeyError: If the provided observer is not registered.
        """
        mapping = self._get_observer_config(observer, publisher)

        state = {}

        if publisher:
            source_keys = mapping["source_keys"]

            for source_name, keys in source_keys.items():

                if observer.is_static_observer() or source_name not in mapping["source_keys"]:
                    source = getattr(self, f"_{source_name}", None)
                else:
                    source = publisher

                if source is not None:
                    for key in keys:
                        value = source.get_state().get(key)

                        if value is not None:
                            state[key] = value

        else:
            # Combine all keys from all publishers
            for publisher_mapping in mapping.values():
                for source_name, keys in publisher_mapping["source_keys"].items():
                    source = getattr(self, f"_{source_name}", None)
                    if source is not None:
                        for key in keys:
                            value = source.get_state().get(key)
                            if value is not None:
                                state[key] = value

        return state

    def _get_observer_config(self, observer: IObserver, publisher: IPublisher = None) -> Dict:
        """
        Retrieves the configuration for a given observer and optionally for a specific publisher.

        If the publisher is provided, the method filters the configuration further based on the publisher type.
        If no publisher is provided, it returns the entire mapping for all publishers related to the observer.

        Args:
            observer (IObserver): The observer requesting the configuration.
            publisher (IPublisher, optional): The publisher that triggered the update. Defaults to None.

        Returns:
            Dict: The configuration dictionary associated with the observer.
                If a publisher is provided, returns only that publisher's configuration.
                If no publisher is provided, returns the full mapping for all publishers.

        Raises:
            KeyError: If no configuration is found for the observer or the specific publisher.
        """
        # Use preloaded source mapping
        observer_name = observer.__class__.__name__

        # Step 1: Filter by Observer
        if observer_name not in self._source_mapping:
            raise KeyError(
                f"No configuration found for observer {observer_name}")

        observer_config = self._source_mapping[observer_name]

        # If no publisher is provided, return all mappings for the observer
        if publisher is None:
            return observer_config

        # Step 2: Filter by Publisher
        publisher_name = publisher.__class__.__name__

        if publisher_name not in observer_config:
            raise KeyError(
                f"No configuration found for observer {observer_name} and publisher {publisher_name}")

        return observer_config[publisher_name]

    def cleanup_observers_for_reload(self) -> None:
        """
        Cleans up observers and views in preparation for reloading a project.
        """
        self._deregister_observers_for_reload()
        self._remove_finalize_views_for_reload()
        self._search_views.clear()

    def _deregister_observers_for_reload(self) -> None:
        """
        Deregisters all observers from their publishers that are marked with 'deregister_on_reload' in the source mapping.
        Uses the same mapping logic as add_observer to ensure all relevant observer instances are removed.
        """
        for observer_name, publisher_configs in self._source_mapping.items():
            for _, config in publisher_configs.items():
                if not config.get("deregister_on_reload", False):
                    continue  # Skip if not marked for deregistration

                # Get all publisher keys from source_keys (same as in add_observer)
                source_keys = config.get("source_keys", {})
                for publisher_key in source_keys.keys():
                    publisher_instance = getattr(
                        self, f"_{publisher_key}", None)
                    if publisher_instance is None:
                        continue

                    # Remove all observer instances of this class from the publisher
                    for observer in publisher_instance._observers[:]:
                        if observer.__class__.__name__ == observer_name:
                            publisher_instance.remove_observer(observer)

    def _remove_finalize_views_for_reload(self) -> None:
        """
        Removes all views that were registered for finalization, except for the MainWindow.
        """
        for view in self._views_to_finalize:
            if view.__class__.__name__ == "MainWindow":
                self._views_to_finalize = [view]
                return

    # initialization

    def register_view(self, view_id: str, view: IView = None) -> None:
        """
        Initializes an Undo/Redo model for a specific view.

        Args:
            view_id (str): The unique identifier for the view for which the
                           Undo/Redo model is being set up.
        """
        if view_id.endswith("_search"):
            self._search_views.append(view)
            return
        if view_id == "main_window":
            self._main_window = view
            return

        self._undo_redo_models[view_id] = UndoRedoModel()
        if view_id == "comparison":
            self._comparison_view = view

    # Perform methods
    # Menu actions
    def perform_menu_new_project(self) -> None:
        """
        Prepares the controller for creating a new project.
        This method resets relevant models and states to ensure a clean slate for project creation.
        """
        self._project_wizard_model.reset()
        self._project_wizard_model.set_project_wizard_type(
            ProjectWizardType.NEW)
        self._main_window.open_project_window(tab=MenuPage.NEW_PROJECT)

    def perform_menu_edit_project(self) -> None:
        """
        Prepares the controller for editing an existing project.
        This method resets relevant models and states to ensure a clean slate for project editing.
        """
        self._project_wizard_model.reset()
        self._project_wizard_model.set_project_wizard_type(
            ProjectWizardType.EDIT)
        self._main_window.open_project_window(tab=MenuPage.EDIT_PROJECT)

    def perform_menu_load_project(self) -> None:
        """
        Prepares the controller for loading an existing project.
        This method resets relevant models and states to ensure a clean slate for project loading.
        """
        print("DEBUG Controller: Opening load project dialog")
        self._main_window.open_load_project_dialog()

    def perform_menu_tag_new_type(self) -> None:
        """
        Prepares the controller for adding a new tag type.
        This method resets relevant models and states to ensure a clean slate for creating a new tag type.
        """
        self._tag_wizard_model.reset()
        self._tag_wizard_model.set_tag_wizard_type(
            TagWizardType.NEW)
        self._main_window.open_tag_editor(MenuPage.NEW_TAG)

    def perform_menu_tag_edit_type(self) -> None:
        """
        Prepares the controller for editing an existing tag type.
        This method resets relevant models and states to ensure a clean slate for editing a tag type.
        """
        self._tag_wizard_model.reset()
        self._tag_wizard_model.set_tag_wizard_type(
            TagWizardType.EDIT)
        self._main_window.open_tag_editor(MenuPage.EDIT_TAG)

    def perform_menu_global_settings(self) -> None:
        """
        Prepares the controller for managing global settings.
        This method can be expanded to include any necessary setup for global settings management.
        """
        self._main_window.open_settings_window(MenuPage.GLOBAL_SETTINGS)

    def perform_menu_project_settings(self) -> None:
        """
        Prepares the controller for managing project-specific settings.
        This method can be expanded to include any necessary setup for project settings management.
        """
        self._main_window.open_project_window(MenuPage.PROJECT_SETTINGS)

    def perform_menu_help(self) -> None:
        """
        Prepares the controller for displaying help information.
        This method can be expanded to include any necessary setup for help management.
        """
        pass

    def perform_menu_about(self) -> None:
        """
        Prepares the controller for displaying about information.
        This method can be expanded to include any necessary setup for about management.
        """
        pass

    # Project Management
    def perform_project_add_tag_group(self, tag_group: dict) -> None:
        """
        Adds a new tag group to the project.
        This method updates the project configuration by adding the specified tag group
        and notifies observers about the change.
        Args:
            tag_group (dict): The tag group to be added, containing group name and tags.
        """
        self._project_wizard_model.add_tag_group(tag_group)

    def perform_project_remove_tag_group(self, group_name: str) -> None:
        """
        Removes a tag group from the project.
        This method updates the project configuration by removing the specified tag group
        and notifies observers about the change.
        Args:
            group_name (str): The name of the tag group to be removed.
        """
        self._project_wizard_model.remove_tag_group(group_name)

    def perform_project_add_tags(self, tags: List[str]) -> None:
        """
        Adds new tags to the project.   
        This method updates the project configuration by adding the specified tags
        and notifies observers about the change.
        Args:
            tags (List[str]): List of tag names to add.
        """
        self._project_wizard_model.add_selected_tags(tags)

    def perform_project_remove_tags(self, selected_indices: List[int]) -> None:
        """
        Removes specified tags from the project.

        This method updates the project configuration by removing the specified tags
        and notifies observers about the change.
        Args:
            selected_indices (List[int]): List of indices of the tags to be removed.
        """
        self._project_wizard_model.remove_selected_tags(selected_indices)

    def update_project_name(self, project_name: str = None) -> None:
        """
        Updates the project name in the project settings model.

        Args:
            project_name (str, optional): The new project name. If None, the last project name is used.
        """
        if not project_name:
            project_name = self._path_manager.get_last_project_name()

        # update the project settings model and path manager with the new project name
        self._project_settings_model.set_project_name(project_name)
        self._path_manager.update_paths(project_name)

    def project_name_exists(self, project_name: str) -> bool:
        """
        Checks if a project with the given name already exists.

        Args:
            project_name (str): The name of the project to check.

        Returns:
            bool: True if the project exists, False otherwise.
        """
        projects = self._project_configuration_manager.get_projects()
        return any(proj["name"] == project_name for proj in projects)

    @check_for_saving_before
    @reset_project_relevant_models
    def perform_project_load_project(self, reload: bool = False, project_name: str = None) -> None:
        """
        Loads the project configuration and updates all relevant models and views.
        Args:
            project_name (str, optional): The name of the project to load. If None,
                                          the current project path is used. Defaults to None.
            reload (bool, optional): Whether to reload the project. Defaults to False.
        Raises:
            FileNotFoundError: If the project configuration file does not exist.
        """
        # update the project name in the project settings model and path manager
        self.update_project_name(project_name)

        # update the suggestion manager with the new tag suggestions accordingly to the current project
        self._suggestion_manager.update_suggestions()
        self._settings_manager.update_settings()
        search_normalization = self._settings_manager.get_search_normalization()
        self._search_manager.set_search_normalization(search_normalization)

        # load the project configuration from the actualized path
        configuration = self._project_configuration_manager.load_configuration()

        self._layout_configuration_model.set_configuration(
            configuration=configuration)

        if reload:
            self._main_window.reload_views_for_new_project()

        for view in self._views_to_finalize:
            view.finalize_view()

        self._file_handler.write_file(
            "last_project", {"last_project": self._project_settings_model.get_state().get(
                "project_name", "")}
        )

        # update all project wizards accordingly
        self.perform_project_update_projects()

    def perform_project_save_project(self) -> None:
        project_data = self._project_wizard_model.get_state()
        # if directories not exist, create them
        project_name = project_data.get("project_name", "")
        self._create_project_directories(project_name)
        # save the project configuration
        # todo complete
        raise NotImplementedError()

    def _create_project_directories(self, project_name: str) -> None:
        """
        Creates the necessary directories for a new project.

        Args:
            project_name (str): The name of the project for which to create directories.
        """
        self._project_directory_manager.create_project_structure(
            project_name)

    def perform_project_update_project_data(self, update_data: Dict[str, Any]) -> None:
        """
        Updates the project data in the project wizard model.
        Args:
            update_data (Dict[str, Any]): A dictionary containing the project data to be updated.
        """
        state = self._project_wizard_model.get_state()
        for key, value in update_data.items():
            if value:
                state[key] = value

        self._project_wizard_model.set_state(state)
        state = self._project_wizard_model.get_state()

    def perform_project_update_projects(self) -> None:
        """
        Updates the list of projects in the edit project wizard model.
        """
        print("DEBUG Controller: Updating project list")
        projects = self._project_configuration_manager.get_projects()
        print(f"DEBUG Controller: Found projects: {projects}")
        available_tags = self._get_available_tags()
        self._project_wizard_model.set_globally_available_tags(available_tags)
        self._project_wizard_model.set_projects(projects)

    def perform_load_project_data_for_editing(self, project_name: str) -> None:
        """
        Loads the project data for editing in the edit project wizard.

        This method retrieves the project configuration and updates the edit project wizard model
        with the project's data, allowing users to modify project settings.

        Args:
            project_name (str): The name of the project to load.
        """
        project_path = self._project_wizard_model.get_project_path(
            project_name)
        project_data = self._file_handler.read_file(project_path)
        selected_tags = [tag.upper()
                         for tag in project_data.get("tags", [])]
        available_tags = self._get_available_tags()
        tag_group_file_name = project_data.get("groups", "")
        tag_groups = self._file_handler.read_file(
            "project_groups", tag_group_file_name) if tag_group_file_name else {}
        editing_data = {
            "project_name": project_data.get("name", ""),
            "available_tags": available_tags,  # todo edit to new date structure
            "selected_tags": selected_tags,
            "tag_group_file_name": tag_group_file_name,
            "tag_groups": tag_groups
        }
        self._project_wizard_model.set_state(
            editing_data, project_wizard_type=MenuPage.EDIT_PROJECT)

    def _get_available_tags(self) -> Dict[str, Dict[str, str]]:
        """
        Retrieves and formats the available tags from the project configuration.

        Returns:
            Dict[str, Dict]: A dictionary mapping formatted tag display names to their details.
        """
        tags = self._project_configuration_manager.get_available_tags()
        available_tags = {
            f"{tag['name'].upper()} ({tag['project']})": tag for tag in tags}

        return available_tags

    @with_highlight_update
    def perform_manual_search(self, search_options: Dict, caller_id: str) -> None:
        """
        Initiates a manual search with the specified parameters.

        This method delegates the execution of a manual search to the search model manager,
        based on user-defined search options such as case sensitivity, whole word matching,
        and regular expressions. The corresponding document model is selected using the caller ID.

        Args:
            search_options (Dict): A dictionary of search parameters with the following keys:
                - 'search_term' (str): The term to search for in the document.
                - 'case_sensitive' (bool): Whether the search should be case-sensitive.
                - 'whole_word' (bool): Whether to match only whole words.
                - 'regex' (bool): Whether the search term should be treated as a regular expression.
            caller_id (str): The identifier of the view or component initiating the search,
                             used to select the appropriate document model.
        """
        # Load the current search model
        self._annotation_mode_model.set_manual_mode()
        document_model = self._comparison_model.get_raw_text_model(
        ) if caller_id == "comparison" else self._document_source_mapping[caller_id]
        self._current_search_model = self._search_model_manager.get_active_model(
            search_type=SearchType.MANUAL, document_model=document_model, options=search_options)
        self._current_search_model.next_result()

        # Update the selection model with the current search result
        self._current_search_to_selection()

    @with_highlight_update
    def perform_start_db_search(self, tag_type: str, caller_id: str) -> None:
        """
        Starts the annotation mode for a specific tag type.

        This method initializes the annotation mode for the specified tag type,
        allowing the user to annotate text with tags of that type. It sets up
        the necessary state and prepares the view for annotation.

        Args:
            tag_type (str): The type of tag to start annotating.
        """
        self._annotation_mode_model.set_auto_mode()
        document_model = self._comparison_model.get_raw_text_model(
        ) if caller_id == "comparison" else self._document_source_mapping[caller_id]

        self._current_search_model = self._search_model_manager.get_active_model(
            tag_type=tag_type,
            search_type=SearchType.DB,
            document_model=document_model
        )
        self._current_search_model.next_result()
        # Update the selection model with the current search result
        self._current_search_to_selection()

    def _current_search_to_selection(self) -> None:
        """
        Updates the selection model with the current search result.

        Args:
            search_model (ISearchModel): The search model containing the current search result.
        """
        search_result = self._current_search_model.get_state().get(
            "current_search_result", None)
        current_selection = {
            "selected_text": search_result.term if search_result else "",
            "position": search_result.start if search_result else -1
        }
        self.perform_text_selected(current_selection)

    def perform_end_search(self) -> None:
        """
        Ends the annotation mode for a specific tag type.

        This method finalizes the auto annotation mode by switching to manual mode
        and deactivating the currently active search model.
        """
        self._annotation_mode_model.set_manual_mode()
        self._search_model_manager.deactivate_active_search_model()
        self._highlight_model.clear_search_highlights()
        if not self._current_search_model:
            return
        self._current_search_model.previous_result()  # Reset to the last result
        self._current_search_model = None

    @with_highlight_update
    def perform_next_suggestion(self) -> None:
        """
        Moves to the next suggestion for the active search type.

        Raises:
            RuntimeError: If no model is active or the active model does not match the tag type.
        """
        if not self._current_search_model:
            raise RuntimeError("No search model is currently active.")
        self._current_search_model.next_result()
        self._current_search_to_selection()

    @with_highlight_update
    def perform_previous_suggestion(self) -> None:
        """
        Moves to the previous suggestion for the active search type.

        Raises:
            RuntimeError: If no model is active or the active model does not match the tag type.
        """
        if not self._current_search_model:
            raise RuntimeError("No search model is currently active.")
        self._current_search_model.previous_result()
        self._current_search_to_selection()

    @with_highlight_update
    def mark_wrong_db_suggestion(self, tag_type: str) -> None:
        """
        Marks the current suggestion as wrong for the specified tag type and deletes it from the search model.
        """
        # load the current suggestion from the search model
        wrong_suggestion = self._current_search_model.get_state().get(
            "current_search_result", None)
        # load wrong suggestions file
        wrong_suggestions = self._file_handler.read_file(
            "project_wrong_suggestions")
        # add current suggestion to wrong suggestions
        wrong_suggestions[tag_type].append(wrong_suggestion)
        # store updated wrong suggestions file
        self._file_handler.write_file(
            "project_wrong_suggestions", wrong_suggestions)
        # Clean up the current search model by deleting the current result
        self._current_search_model.delete_current_result()

    def perform_pdf_extraction(self, extraction_data: dict) -> None:
        """
        Extracts text from a PDF file and updates the preview document model.

        Constructs a basic document dictionary for extraction mode.

        Args:
            extraction_data (dict): A dictionary containing parameters for PDF extraction:
                - "pdf_path" (str): Path to the PDF file (required).
                - "page_margins" (str): Margins to apply to the pages (optional).
                - "page_ranges" (str): Specific page ranges to extract (optional).
        """
        extracted_text = self._pdf_extraction_manager.extract_document(
            extraction_data=extraction_data)
        pdf_path = extraction_data["pdf_path"]
        file_name = self._file_handler.derive_file_name(pdf_path)

        print(
            f"Extracted text from {pdf_path} with {len(extracted_text)} characters.")
        print(f"File name derived: {file_name}")
        document = {
            "file_name": file_name,
            "file_path": "",  # no path settet until save
            "document_type": "extraction",
            "meta_tags": {},
            "text": extracted_text
        }

        self._extraction_document_model.set_document(document)

    def perform_text_adoption(self) -> None:
        """
        Initiates the text adoption after extraction.
        """
        self.perform_export()
        self.set_active_view("annotation")
        self._layout_configuration_model.set_active_notebook_index(1)

    def perform_update_preview_text(self, text: str) -> None:
        """
        Updates the text content of the preview document model.

        This method sets the provided text as the new content of the preview document model,
        triggering updates to its observers.

        Args:
            text (str): The new text content to update in the preview document model.

        Updates:
            - The text in the preview document model is updated, and its observers are notified.
        """
        self._extraction_document_model.set_text(text)

    def perform_update_meta_tags(self, tag_strings: Dict[str, str]) -> None:
        """
        Updates multiple meta tags in the model.

        Args:
            tag_strings (Dict[str, str]): A dictionary where keys are meta tag types
                                          and values are their corresponding new values.

        This method updates the meta tags in the model, applying the provided
        key-value pairs to modify the current state of the metadata.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        self._tag_manager.set_meta_tags(tag_strings, target_model)

    @with_highlight_update
    def perform_add_tag(self, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an AddTagCommand to add a new tag to the tag manager.

        This method augments the provided tag data with the appropriate ID attribute name
        based on the tag type, constructs a command object, and executes it via the
        undo/redo mechanism for the active document view.

        Args:
            tag_data (Dict): A dictionary containing the tag attributes. Must include:
                - "tag_type" (str): The type of the tag.
                - "attributes" (Dict[str, str]): The tag's attributes.
                - "position" (int): The position of the tag in the text.
                - "text" (str): The inner text of the tag.
                - "references" (Dict[str, str]): Optional reference attributes.
                - "equivalent_uuids" (List[str]): Optional UUID equivalence list.
                - "uuid" (str): Optional UUID (generated if missing).
            caller_id (str): The unique identifier of the view initiating the action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        tag_data["id_name"] = self._layout_configuration_model.get_id_name(
            tag_data.get("tag_type"))
        command = AddTagCommand(
            self._tag_manager, tag_data, target_model=target_model, caller_id=caller_id)
        self._execute_command(command=command, caller_id=caller_id)

    @with_highlight_update
    def perform_edit_tag(self, tag_id: str, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an EditTagCommand to modify an existing tag in the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be edited.
            tag_data (Dict): A dictionary containing the updated data for the tag.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        tag_data["id_name"] = self._layout_configuration_model.get_id_name(
            tag_data.get("tag_type"))
        tag_uuid = self._tag_manager.get_uuid_from_id(tag_id, target_model)
        command = EditTagCommand(
            self._tag_manager, tag_uuid, tag_data, target_model)
        self._execute_command(command=command, caller_id=caller_id)

    @with_highlight_update
    def perform_delete_tag(self, tag_id: str, caller_id: str) -> None:
        """
        Creates and executes a DeleteTagCommand to remove a tag from the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be deleted.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        tag_uuid = self._tag_manager.get_uuid_from_id(tag_id, target_model)

        # Check if the tag can be deleted before creating the command
        if self._tag_manager.is_deletion_prohibited(tag_uuid, target_model):
            self._handle_failure(FailureReason.TAG_IS_REFERENCED)
            return

        # Create and execute the delete command since deletion is allowed
        command = DeleteTagCommand(self._tag_manager, tag_uuid, target_model)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_text_selected(self, selection_data: Dict) -> None:
        """
        Updates the selection model with the newly selected text, its position, and suggested attributes.

        This method is triggered when text is selected in the view and updates
        the selection model to reflect the new selection, including possible attribute
        and ID suggestions based on the selected text and existing document data.

        Args:
            selection_data (Dict): A dictionary containing:
                - "selected_text" (str): The selected text.
                - "position" (int): The starting position of the selected text in the document.

        Updates:
            - The `selected_text`, `selected_position`, and `suggestions` attributes in the selection model.
            - `suggestions` contains attribute and ID recommendations based on the selected text
              and existing IDs in the document.
        """
        if self._active_view_id == "extraction":
            return
        selected_text = selection_data["selected_text"]
        document_model = self._document_source_mapping[self._active_view_id]
        selection_data["suggestions"] = self._suggestion_manager.get_suggestions(
            selected_text, document_model)
        self._selection_model.set_selected_text_data(selection_data)

    @check_for_saving_before
    @with_highlight_update
    @reset_search
    def perform_open_file(self) -> None:
        """
        Handles the process of opening files and updating the appropriate document model based on the active view.

        This method processes the provided file paths, determines the active view, and updates the corresponding
        document model with the file data. The behavior depends on the active view:
        - For the "extraction" view, the file path is set directly in the extraction document model.
        - For the "annotation" view, the file is read and loaded into the annotation document model.
        - For the "comparison" view, multiple files are processed if necessary, and the comparison document model is updated.

        Args:
            file_paths (List[str]): A list of file paths selected by the user.
                                    For single-file operations, only the first file is used.

        Behavior:
            - **Extraction View**: Updates the extraction document model with the file path.
            - **Annotation View**: Reads the file and updates the annotation document model with its content.
            - **Comparison View**: Processes multiple files if provided, or verifies if the document type is suitable
              for comparison, then updates the comparison document model.

        Notes:
            - If multiple file paths are provided in the "comparison" view, they are processed together.
            - If the document's type is not "comparison" in the "comparison" view, additional processing is performed.

        Raises:
            ValueError: If `file_paths` is empty or the active view ID is invalid.
        """

        # Reset old state
        self._reset_undo_redo(self._active_view_id)

        # Determine the load configuration based on the active view
        if self._active_view_id == "extraction":
            load_config = {
                "config": {
                    "initialdir": self._file_handler.resolve_path("default_extraction_load_folder"),
                    "filetypes": [("PDF Files", "*.pdf")],
                    "title": "Open PDF for Extraction"
                },
                "mode": "single"}
        elif self._active_view_id == "annotation":
            load_config = {
                "config": {
                    "initialdir": self._file_handler.resolve_path("default_annotation_load_folder"),
                    "filetypes": [("JSON Files", "*.json")],
                    "title": "Open JSON for Annotation"
                },
                "mode": "single"
            }
        elif self._active_view_id == "comparison":
            load_config = {
                "config": {
                    "initialdir": self._file_handler.resolve_path("default_comparison_load_folder"),
                    "filetypes": [("JSON Files", "*.json")],
                    "title": "Open JSON for Comparison"
                },
                "mode": "multiple"
            }
        else:
            raise ValueError(f"Invalid active view ID: {self._active_view_id}")

        file_paths = self._main_window.ask_user_for_file_paths(
            load_config=load_config)

        if not file_paths:
            raise ValueError("No file paths provided for opening files.")

        # load document
        file_path = file_paths[0]
        if self._active_view_id == "extraction":
            self._extraction_document_model.set_file_path(file_path=file_path)
            return

        documents = [self._file_handler.read_file(
            file_path=file_path) for file_path in file_paths]
        for document, path in zip(documents, file_paths):
            document["file_path"] = path

        if self._active_view_id == "annotation":
            if len(documents) != 1:
                raise ValueError(
                    "Too many files selected: Only one file path is allowed when loading a predefined annotation model.")
            self._annotation_document_model.set_document(documents[0])
            self._tag_manager.extract_tags_from_document(
                self._annotation_document_model)

        # Load stored comparison_model or set up a new one from multiple documents
        if self._active_view_id == "comparison":
            if documents[0]["document_type"] == "comparison":
                if len(documents) > 1:
                    raise ValueError(
                        "Too many files selected: Only one file path is allowed when loading a predefined comparison model.")
                self._load_comparison_model(documents[0])
            else:
                self._setup_comparison_model(documents)
        self._save_state_model.reset_key(self._active_view_id)

    def perform_save(self, file_path: str = None, view_id: str = None) -> None:
        view_id = view_id or self._active_view_id
        source_model = self._document_source_mapping[view_id]
        document = source_model.get_state()

        # Try user-specified file_path, otherwise use document's path
        file_path = file_path or document.get("file_path")

        if not file_path:
            self.perform_save_as()
            return

        if self._file_handler.check_overwriting(file_path):
            if not self._main_window.ask_user_for_overwrite_confirmation(file_path):
                self.perform_save_as()
                return

        # prepare data for saving
        if not view_id == "comparison":
            document_data = {"document_type": view_id,
                             "file_path": file_path,
                             "file_name": self._file_handler.derive_file_name(file_path),
                             "meta_tags": {
                                 tag_type: [
                                     ", ".join(str(tag) for tag in tags)]
                                 for tag_type, tags in document.get("meta_tags", {}).items()
                             },
                             "text": document["text"]}
        else:
            merged_document = document.get("merged_document", {})
            # prepare data for comparison view
            document_data = {
                "document_type": "comparison",
                "source_paths": document["source_file_paths"],
                "source_file_names": document.get("file_names", []),
                "file_path": file_path,
                "num_sentences": document.get("num_sentences", 0),
                "current_sentence_index": document.get("current_sentence_index", 0),
                "comparison_sentences": document.get("comparison_sentences", []),
                "adopted_flags": document.get("adopted_flags", []),
                "differing_to_global": document.get("differing_to_global", []),
                "document_data": {
                    "document_type": "annotation",
                    "file_name": merged_document.get_file_name(),
                    "file_path": merged_document.get_file_path(),
                    "meta_tags": {
                        tag_type: [", ".join(str(tag) for tag in tags)]
                        for tag_type, tags in merged_document.get_meta_tags().items()
                    },
                    "text": merged_document.get_text(),
                }
            }

        if document_data:
            self._file_handler.write_file(file_path, document_data)
        else:
            raise ValueError(
                "No valid document data found for saving. Ensure the active view is set correctly.")

    def perform_save_as(self) -> None:
        """
        Opens a save-as dialog to let the user choose a file path, then saves the current document.
        """
        initial_dir = self._file_handler.resolve_path(
            f"default_{self._active_view_id}_save_folder")
        file_path = self._main_window.ask_user_for_save_path(
            initial_dir=initial_dir)
        if file_path:
            self.perform_save(file_path=file_path)

    def check_for_saving(self, enforce_check: bool = False) -> None:
        """
        Checks the SaveStateModel for any dirty (unsaved) views and prompts the user
        via the main window whether they want to save each of them.

        If the user chooses to save, the corresponding document is saved using
        `perform_save(view_id)`.

        Assumes:
            - self._save_state_model provides get_dirty_keys()
            - self._main_window has method prompt_save(view_id: str) -> bool
            - self.perform_save(view_id: str) exists and handles saving
        """
        dirty_keys = self._save_state_model.get_dirty_keys()
        if not enforce_check and self._active_view_id not in dirty_keys:
            return
        for view_id in dirty_keys:
            should_save = self._main_window.prompt_save(view_id)
            if should_save:
                self.perform_save(view_id=view_id)

    def perform_export(self) -> None:
        """
        Exports the current document based on the active view.

        Raises:
            ValueError: If the active view ID is not supported for export.

        """
        state = self._document_source_mapping[self._active_view_id].get_state()
        if self._active_view_id == "extraction":
            self._export_extracted_document(state)

        elif self._active_view_id == "comparison":
            self._export_comparison_document(state)
        else:
            raise ValueError(
                f"Export is not supported in view mode '{self._active_view_id}'.")

    def _export_extracted_document(self, state: dict) -> None:
        """
        Exports the extracted document from the extraction view.

        Args:
            state (dict): The current state of the extraction document model.
        """
        document = state
        file_name = document.get("file_name", "")
        file_path = self._file_handler.resolve_path(
            "default_extraction_save_folder", file_name + ".json")
        file_path = self._solve_overwriting(file_path)
        save_document = {
            "document_type": "annotation",
            "file_name": file_name,
            "file_path": file_path,
            "meta_tags": document.get("meta_tags", {}),
            "text": document.get("text", ""),
        }
        self._annotation_document_model.set_document(save_document)
        self._file_handler.write_file(file_path, save_document)
        return

    def _export_comparison_document(self, state: dict) -> None:
        """
        Exports the merged document from the comparison view.

        Args:
            state (dict): The current state of the comparison model containing the merged document.

        Raises:
            ValueError: If no merged document is found in the comparison state or if the file path 
        """
        merged_document = state.get("merged_document")
        if not merged_document:
            raise ValueError(
                "No merged document found in the comparison state. Cannot export.")
        file_path = merged_document.get_file_path()
        if not file_path:
            initial_dir = self._file_handler.resolve_path(
                f"default_merged_save_folder")
            file_path = self._main_window.ask_user_for_save_path(
                initial_dir=initial_dir)
            file_name = self._file_handler.derive_file_name(
                file_path)
            self._comparison_model.set_merged_document_file_name(file_name)
            self._comparison_model.set_merged_document_file_path(file_path)
        file_path = self._solve_overwriting(file_path)
        file_name = self._file_handler.derive_file_name(
            file_path)
        save_document = {
            "document_type": "annotation",
            "file_name": file_name,
            "file_path": file_path,
            "meta_tags": {
                tag_type: [", ".join(str(tag) for tag in tags)]
                for tag_type, tags in merged_document.get_meta_tags().items()
            },
            "text": merged_document.get_text(),
        }
        self._file_handler.write_file(file_path, save_document)
        return

    def _solve_overwriting(self, file_path) -> str:
        """
        Checks if the current file path is valid for overwriting.

        Returns:
            str: The resolved file path, which may be updated based on user input.
        """
        if self._file_handler.check_overwriting(file_path):
            if not self._main_window.ask_user_for_overwrite_confirmation(file_path):
                initial_dir = self._file_handler.resolve_path(
                    f"default_{self._active_view_id}_save_folder")
                file_path = self._main_window.ask_user_for_save_path(
                    initial_dir=initial_dir)
        return file_path

    def _setup_comparison_model(self, documents) -> None:
        self._layout_configuration_model.set_num_comparison_displays(
            len(documents)+1)

        document_models = [AnnotationDocumentModel()]+[AnnotationDocumentModel(
            document) for document in documents]
        highlight_models = [HighlightModel() for _ in document_models]
        for document_model in document_models:
            self._tag_manager.extract_tags_from_document(document_model)
        self._comparison_model.set_document_models(document_models)
        self._comparison_model.set_highlight_models(highlight_models)
        #! Don't change the order since the documents trigger the displaycreation
        comparison_displays = self._comparison_view.get_comparison_displays()
        self._comparison_model.register_comparison_displays(
            comparison_displays)

        comparison_data = self._comparison_manager.extract_comparison_data(
            document_models[1:])
        self._comparison_model.set_comparison_data(
            comparison_data)

    def _load_comparison_model(self, document: dict) -> None:
        """
        Reconstructs the comparison model from a previously saved file.

        Loads source documents and the merged document (annotation), restores the internal
        comparison model state, and sets up the displays and tag data.

        Args:
            document (dict): The loaded comparison document data from file.
        """
        # Step 0: Reset old state
        self._reset_undo_redo("comparison")

        # Step 1: Load document models from stored paths
        source_paths = document["source_paths"]
        source_documents_data = [
            self._file_handler.read_file(path) for path in source_paths]

        raw_model = AnnotationDocumentModel()
        annotator_models = [AnnotationDocumentModel(
            data) for data in source_documents_data]
        document_models = [raw_model] + annotator_models

        highlight_models = [HighlightModel() for _ in document_models]
        for document_model in document_models:
            self._tag_manager.extract_tags_from_document(document_model)
        self._comparison_model.set_document_models(document_models)
        self._comparison_model.set_highlight_models(highlight_models)

        # Step 4: Setup displays
        self._layout_configuration_model.set_num_comparison_displays(
            len(document_models))
        displays = self._comparison_view.get_comparison_displays()
        self._comparison_model.register_comparison_displays(displays)

        # Step 5: Load merged model from inlined `document_data`
        merged_document_data = document["document_data"]
        merged_model = AnnotationDocumentModel(merged_document_data)

        # Step 6: Prepare and set comparison data
        comparison_sentences = document.get("comparison_sentences", [])
        current_index = document.get("current_sentence_index", 0)
        start_data = self._comparison_manager.get_start_data(
            sentence_index=current_index,
            comparison_sentences=comparison_sentences
        )

        comparison_data = {
            "merged_document": merged_model,
            "comparison_sentences": comparison_sentences,
            "differing_to_global": document.get("differing_to_global", []),
            "start_data": start_data,
        }
        self._comparison_model.set_comparison_data(comparison_data)

        # Step 7: Restore internal flags and index
        self._comparison_model._current_index = current_index
        self._comparison_model._adopted_flags = document.get(
            "adopted_flags", [False] * len(comparison_sentences)
        )

    def extract_tags_from_document(self, documents) -> None:
        """
        Extracts tags for all given documents and stores them in their corresponding models.

        Args:
            documents (List[IDocumentModel]): A list of document models to extract tags from.
        """
        for document in documents:
            self._tag_manager.extract_tags_from_document(document)

    #! DEPRECATED

    def find_equivalent_tags(self, documents: List[IDocumentModel], merged_document: IDocumentModel) -> None:
        """
        Identifies and marks equivalent tags across multiple document versions.

        This method analyzes tags across all annotator documents and the merged document
        to determine equivalence based on structure and content. It updates each tag
        with a list of UUIDs representing all of its equivalent counterparts.

        Args:
            documents (List[IDocumentModel]): The annotator-specific document models.
            merged_document (IDocumentModel): The merged reference document.

        Side Effects:
            Each tag in the documents and the merged document will be updated via
            `set_equivalent_uuids()` to include the UUIDs of all semantically
            equivalent tags across versions.
        """
        documents_tags = [document.get_tags() for document in documents]
        merged_document_tags = merged_document.get_tags()
        separator = '\n\n'
        documents_sentences = [document.get_text().split(separator)
                               for document in documents]
        merged_sentences = merged_document.get_text().split(separator)

        for index, merged_sentence in enumerate(merged_sentences):
            sentences = [document_sentences[index]
                         for document_sentences in documents_sentences]
            self._tag_manager.find_equivalent_tags(
                sentences=sentences, common_sentence=merged_sentence, documents_tags=documents_tags, merged_tags=merged_document_tags)
    #! END DEPRECATED

    @with_highlight_update
    def perform_prev_sentence(self) -> None:
        """
        Moves the comparison model to the previous sentence and updates documents.
        """
        self._shift_and_update(self._comparison_model.previous_sentences)

    @with_highlight_update
    def perform_next_sentence(self) -> None:
        """
        Moves the comparison model to the next sentence and updates documents.
        """
        self._shift_and_update(self._comparison_model.next_sentences)

    def _shift_and_update(self, sentence_func: Callable[[], List[str]]) -> None:
        """
        Internal helper to shift the current sentence and update the documents.

        Args:
            sentence_func (Callable[[], List[str]]): Function to retrieve the target sentence(s).
        """
        sentences = sentence_func()
        tags = [[TagModel(tag_data) for tag_data in self._tag_processor.extract_tags_from_text(
            sentence)] for sentence in sentences]
        self._comparison_model.update_documents(sentences, tags)

    def perform_adopt_annotation(self, adoption_index: int) -> None:
        """
        Performs the adoption of an annotated sentence by creating and executing
        an AdoptAnnotationCommand using data provided by the comparison model.

        Args:
            adoption_index (int): Index of the annotator whose sentence is adopted.
        """
        adoption_data = self._comparison_model.get_adoption_data(
            adoption_index)

        # check if sentences is already adopted
        if adoption_data["is_adopted"]:
            self._handle_failure(FailureReason.IS_ALREADY_ADOPTED)
            # comparison_state = self._comparison_model.get_adoption_data(
            #     adoption_index)
            # current_index = self._comparison_model._current_index
            return

        # check if sentence contains references, since it is not possible to resolve references yet.
        adoption_sentence = adoption_data["sentence"]
        if self._tag_processor.is_sentence_unmergable(
                adoption_sentence):
            self._handle_failure(FailureReason.COMPARISON_MODE_REF_NOT_ALLOWED)
            return

        command = AdoptAnnotationCommand(
            tag_manager=self._tag_manager,
            tag_models=adoption_data["sentence_tags"],
            target_model=adoption_data["target_model"],
            comparison_model=self._comparison_model
        )
        self._execute_command(command=command, caller_id="comparison")
        self.perform_next_sentence()

    def perform_create_color_scheme(self, colorset_name: str = "viridis", complementary_search_color: bool = False) -> None:
        """
        Creates a color scheme for the tag types defined in the configuration.
        This method uses the color manager to generate a color scheme based on the
        tag types specified in the current configuration.
        Args:
            colorset_name (str): The name of the color set to use. Defaults to "viridis".
        Raises:
            ValueError: If the colorset_name is not recognized or supported.
        """
        self._color_manager.create_color_scheme(tag_keys=self._project_configuration_manager.load_configuration()['layout'][
            'tag_types'], colorset_name=colorset_name, complementary_search_color=complementary_search_color)

    # Helpers

    def _handle_failure(self, reason: FailureReason) -> None:
        """
        Handles a failed user action by showing an appropriate message box
        based on the provided FailureReason.

        Args:
            reason (FailureReason): The specific reason why the action failed.
                                    Determines the message shown to the user.

        Side Effects:
            Displays a warning or error dialog using tkinter.messagebox.

        """
        if reason == FailureReason.TAG_IS_REFERENCED:
            mbox.showerror("Action not allowed",
                           "This tag is still referenced and cannot be deleted.")
        elif reason == FailureReason.COMPARISON_MODE_REF_NOT_ALLOWED:
            mbox.showwarning("Action not allowed",
                             "Tags with references cannot be inserted in comparison mode.")
        elif reason == FailureReason.NESTED_TAGS:
            mbox.showwarning("Action not allowed",
                             "Tags can't be nested.")
        elif reason == FailureReason.IS_ALREADY_ADOPTED:
            mbox.showwarning("Action not allowed",
                             "These Sentence is already adopted.")
        # add more cases as needed

    def _reset_undo_redo(self, view_id) -> None:
        """
        Clears both the undo and redo stacks.

        This method resets the state by removing all stored undo and redo actions,
        effectively discarding any command history.

        Args:
            view_id (str): The unique identifier of the view for which the undo/redo stacks should be reset.
        """
        self._undo_redo_models[view_id].reset()
# Getters/setters

    def get_selected_text_data(self) -> Dict:
        """
        Retrieves the currently selected text data from the selection model.

        This method accesses the selection model to fetch the current selected
        text and its starting position.

        Returns:
            Dict: A dictionary containing the selected text and its position with the following keys:
                - "text" (str): The currently selected text.
                - "position" (int): The starting position of the selected text in the document.
        """
        return self._selection_model.get_state()

    def get_active_view(self) -> str:
        """
        Returns the unique identifier of the currently active view.

        This method provides the view ID of the view that is currently focused
        and interacting with the user. It is used to ensure that actions such as
        undo and redo are applied to the correct view.

        Returns:
            str: The unique identifier of the active view.
        """
        return self._active_view_id

    def set_active_view(self, view_id: str) -> None:
        """
        Sets the active view for shortcut handling.

        Args:
            view_id (str): The unique identifier of the currently active view.
        """
        self._active_view_id = view_id

        index_mapping = {
            "extraction": 0,
            "annotation": 1,
            "comparison": 2
        }

        index = index_mapping.get(view_id)
        if index is not None:
            self._layout_configuration_model.set_active_notebook_index(index)

    def get_file_path(self) -> str:
        """
        Retrieves the file path from the current active data source.

        The method identifies the appropriate data source based on the active view ID
        and retrieves the file name associated with it.

        Returns:
            str: The file path of the current active data source.
        """
        data_source = self._document_source_mapping[self._active_view_id]
        return data_source.get_file_path()

    def get_highlight_data(self, target_model: IPublisher = None) -> List[Tuple[str, int, int]]:
        """
        Retrieves the highlight data for text annotation or search results.

        If the target model is an IDocumentModel, this method fetches annotation highlights.
        If the target model is an ISearchModel, it fetches search result highlights.

        Returns:
            List[Tuple[str, int, int]]: A list of tuples where:
                - The first element (str) is the highlight color.
                - The second element (int) is the start position in characters.
                - The third element (int) is the end position in characters.
        """

        if isinstance(target_model, IDocumentModel):
            color_scheme = self._settings_manager.get_color_scheme()["tags"]
            highlight_data = self._tag_manager.get_highlight_data(target_model)
            return [
                (color_scheme[tag], start, end) for tag, start, end in highlight_data
            ]
        # todo add search highlights

        elif isinstance(target_model, ISearchModel):
            current_search_color = self._settings_manager.get_color_scheme()[
                "current_search"]["background_color"]
            search_state = target_model.get_state()
            current_search_result = search_state.get(
                "current_search_result", None)
            highlight_data = [
                (current_search_color, current_search_result.start, current_search_result.end)]
            if self._settings_manager.are_all_search_results_highlighted():
                # If all search results should be highlighted, add them to the highlight data
                search_color = self._settings_manager.get_color_scheme()[
                    "search"]["background_color"]
                highlight_data += [(search_color, result.start, result.end)
                                   for result in search_state.get("results", []) if result != current_search_result]
            if self._active_view_id == "annotation":
                document_model = self._annotation_document_model
            if self._active_view_id == "comparison":
                document_model = self._comparison_model.get_raw_text_model()
            color_scheme = self._settings_manager.get_color_scheme()["tags"]
            tag_data = self._tag_manager.get_highlight_data(
                document_model)
            tag_highlights = [
                (color_scheme[tag], start, end) for tag, start, end in tag_data
            ]
            highlight_data += tag_highlights
            return highlight_data

        return []

    def _update_highlight_model(self) -> None:
        """
        Updates the highlight model with tag and search highlights based on the current active view.
        """
        color_scheme = self._settings_manager.get_color_scheme()
        if self._active_view_id == "annotation":
            document_models = [
                self._document_source_mapping[self._active_view_id]]
            highlight_models = [self._highlight_model]

        if self._active_view_id == "comparison":
            comparison_model = self._document_source_mapping[self._active_view_id]
            document_models = comparison_model.get_document_models()
            highlight_models = comparison_model.get_highlight_models()

        for document_model, highlight_model in zip(document_models, highlight_models):
            highlight_data = self._tag_manager.get_highlight_data(
                document_model)
            tag_highlights = [(color_scheme["tags"][tag]["background_color"], color_scheme["tags"][tag]["font_color"], start, end) for tag, start, end in highlight_data
                              ]
            highlight_model.add_tag_highlights(tag_highlights)

        if not self._current_search_model:
            return

        search_highlights = []

        current_search_bg_color = color_scheme["current_search"]["background_color"]
        current_search_font_color = color_scheme["current_search"]["font_color"]
        search_state = self._current_search_model.get_state()
        current_search_result = search_state.get(
            "current_search_result", None)

        if self._settings_manager.are_all_search_results_highlighted():
            search_bg_color = color_scheme["search"]["background_color"]
            search_font_color = color_scheme["search"]["font_color"]
            results = search_state.get("results", [])
            search_highlights += [
                (search_bg_color, search_font_color, r.start, r.end)
                for r in results
                if r != current_search_result
            ]

        # Ensure current search result is always highlighted on top, with its specific color
        if current_search_result:
            search_highlights.append(
                (current_search_bg_color, current_search_font_color, current_search_result.start,
                 current_search_result.end)
            )
        highlight_models[0].add_search_highlights(search_highlights)

    def get_tag_types(self) -> List[str]:
        """
        Retrieves all available tag types from the loaded template groups.

        This method iterates through the template groups and collects unique
        tag types used within the templates.

        Returns:
            List[str]: A list of unique tag types used in the current project.
        """
        return self._layout_configuration_model.get_tag_types()

    def get_id_name(self, tag_type: str) -> str:
        """
        Retrieves the name of the ID attribute for a given tag type.

        This method returns the attribute name that serves as the unique identifier
        for a tag of the specified type.

        Args:
            tag_type (str): The type of the tag whose ID attribute name is requested.

        Returns:
            str: The name of the ID attribute for the given tag type. Returns an empty string
                 if no ID attribute is defined for the tag type.
        """
        return self._layout_configuration_model.get_id_name(tag_type)

    def get_id_refs(self, tag_type: str) -> str:
        """
        Retrieves the ID references for a given tag type.

        This method returns the attribute name that serves as the unique identifier
        for a tag of the specified type.

        Args:
            tag_type (str): The type of the tag whose ID attribute name is requested.

        Returns:
            List[str]: A list of all attributes with an ID for the given tag type.
        """
        return self._layout_configuration_model.get_id_refs(tag_type)

    def get_id_prefixes(self) -> Dict[str, str]:
        """
        Retrieves a dictionary, which maps the tag types to the id prefixes

        Returns:
            Dict[str,str]: A Dict which maps the tag types to the id prefixes.
        """
        return self._layout_configuration_model.get_id_prefixes()

    def get_align_option(self) -> str:
        """
        Retrieves the alignment option from the default comparison settings.

        This method reads the comparison settings file and extracts the
        alignment option, which determines whether texts should be merged
        using "union" or "intersection".

        Returns:
            str: The alignment option, either "union" or "intersection".

        Raises:
            KeyError: If the "align_option" key is missing from the settings.
            FileNotFoundError: If the comparison settings file cannot be found.
        """
        key = "default_comparison_settings"
        comparison_settings_path = self._file_handler.resolve_path(key)
        comparison_settings = self._file_handler.read_file(
            comparison_settings_path)
        align_option = comparison_settings["align_option"]
        return align_option

    def get_abbreviations(self) -> set[str]:
        """
        Retrieves a set of abbreviations for the current languages from the settings manager.

        This method loads the abbreviations from the project abbreviations file and combines
        them into a single set based on the current languages specified in the settings manager.

        Returns:
            set[str]: A set containing all abbreviations for the specified languages.

        Raises:
            KeyError: If any of the provided keys are missing in the JSON file.
        """
        return self._settings_manager.get_abbreviations()
