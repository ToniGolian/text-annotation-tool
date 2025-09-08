from typing import Dict, List
from enums.wizard_types import ProjectWizardType
from observer.interfaces import IPublisher


class ProjectWizardModel(IPublisher):
    """
    Model for managing project configuration data during project creation or editing.

    This model holds the state of the project being defined or modified through the wizard.
    It inherits from IPublisher and notifies observers whenever the state changes.
    """

    def __init__(self) -> None:
        """
        Initializes the model with empty project settings.
        """
        super().__init__()
        self._set_defaults()

    def _set_defaults(self) -> None:
        """
        Resets the model to its initial empty state and notifies observers.
        """
        self._projects = []
        self._project_name = ""
        # [{name: str, path: str,display_name: str,project: str}]
        self._globally_available_tags = []
        self._selected_tags_display_names = []
        self._locally_available_tags = []
        self._locally_available_tags_display_names = []
        self._tag_group_file_name = ""
        self._tag_groups = {}
        self._project_wizard_type = None
        self.notify_observers()

    def set_state(self, state: dict) -> None:
        """
        Sets the internal state from a dictionary and notifies observers.

        Args:
            state (dict): Dictionary containing keys:
                'project_name', 'available_tags', 'selected_tags',
                'tag_group_file_name', 'tag_groups'
        """
        self._project_name = state.get("project_name", "")
        self._globally_available_tags = state.get(
            "globally_available_tags", [])
        self._selected_tags_display_names = state.get("selected_tags", [])
        self._tag_group_file_name = state.get("tag_group_file_name", "")
        self._tag_groups = state.get("tag_groups", {})
        self._update_locally_available_tags()
        self.notify_observers()

    def get_state(self) -> dict:
        """
        Returns the current project configuration as a dictionary.

        Returns:
            dict: Dictionary of all project settings.
        """
        state = {
            "projects": self._projects,
            "project_name": self._project_name,
            "globally_available_tags":  self._globally_available_tags,
            "locally_available_tags": self._locally_available_tags_display_names,
            "selected_tags": self._selected_tags_display_names,
            "tag_group_file_name": self._tag_group_file_name,
            "tag_groups": self._tag_groups,
            "project_wizard_type": self._project_wizard_type
        }
        return state

    def add_tag_group(self, tag_group: Dict[str, List[str]]) -> None:
        """
        Adds a new tag group to the internal state and notifies observers.

        Args:
            tag_group (Dict[str, List[str]]): The tag group to add, containing the group name and associated tags.
        """
        group_name = tag_group.get("name")
        tags = tag_group.get("tags", [])
        if group_name:
            self._tag_groups[group_name] = tags
            self.notify_observers()

    def delete_tag_group(self, group_name: str) -> None:
        """
        Deletes a tag group from the internal state and notifies observers.

        Args:
            group_name (str): Name of the tag group to be removed.
        """
        if group_name in self._tag_groups:
            del self._tag_groups[group_name]
            self.notify_observers()

    def get_project_build_data(self) -> dict:
        """
        Constructs a dictionary containing all relevant data for building the project.

        Returns:
            dict: A dictionary with the following structure:
                {
                    "project_name": str,
                    "tag_group_file_name": str,
                    "groups": dict[str, list[str]],
                    "selected_tags": list[dict[str, str]]  # List of selected tag dictionaries
                }
        """
        selected_tags = [
            {
                "name": tag["name"],
                "path": tag["path"],
                "display_name": tag["display_name"],
                "project": tag["project"]
            } for tag in self._globally_available_tags
            if tag["display_name"] in self._selected_tags_display_names]

        return {
            "project_name": self._project_name,
            "tag_group_file_name": self._tag_group_file_name,
            "groups": self._tag_groups,
            "selected_tags": selected_tags
        }

    def _clean_name(self, name: str) -> str:
        """
        Cleans the tag name by removing any text in parentheses and converting to uppercase.
        Leading and trailing whitespace is also removed.

        Args:
            name (str): The tag name to clean.

        Returns:
            str: The cleaned and normalized tag name.
        """
        if not name:
            return ""
        cleaned = name.split("(")[0].strip()
        return cleaned.upper()

    def set_project_name(self, name: str) -> None:
        """
        Sets the project name and notifies observers.

        Args:
            name (str): The new project name.
        """
        self._project_name = name.strip()
        self.notify_observers()

    def set_tag_group_file_name(self, file_name: str) -> None:
        """
        Sets the tag group file name and notifies observers.

        Args:
            file_name (str): The new tag group file name.
        """
        self._tag_group_file_name = file_name.strip()
        self.notify_observers()

    def set_projects(self, projects: List[str]) -> None:
        """
        Sets the list of available projects and notifies observers.

        Args:
            projects (List[str]): List of project names.
        """
        self._projects = projects
        self.notify_observers()

    def add_selected_tags(self, tags: List[str]) -> None:
        """
        Adds the given tags to the selected tags list and notifies observers.

        Args:
            tags (list[str]): List of tag names to add.
        """
        self._selected_tags_display_names.extend(tags)
        self._selected_tags_display_names.sort()
        self._update_locally_available_tags()
        self.notify_observers()

    def remove_selected_tags(self, selected_indices: List[int]) -> None:
        """
        Removes specified tags from the selected tags list by index and notifies observers.

        Args:
            selected_indices (List[int]): List of indices of tags to remove.
        """
        self._selected_tags_display_names = [
            tag for i, tag in enumerate(self._selected_tags_display_names) if i not in selected_indices
        ]
        self._update_locally_available_tags()
        self.notify_observers()

    def _update_locally_available_tags(self) -> None:
        """
        Updates the list of locally available tags by excluding selected tags from globally available tags.
        """
        self._locally_available_tags = [
            item for item in self._globally_available_tags if item["display_name"] not in self._selected_tags_display_names
        ]

        self._locally_available_tags_display_names = self._retrieve_display_names(
            self._locally_available_tags)

    def _retrieve_display_names(self, tags: List[Dict[str, str]]) -> List[str]:
        """
        Retrieves the display names from a list of tag dictionaries.

        Args:
            tags (List[Dict[str, str]]): List of tag dictionaries.

        Returns:
            List[str]: List of display names.
        """

        return sorted([tag["display_name"] for tag in tags if "display_name" in tag])

    def get_project_path(self, name: str) -> str:
        """
        Retrieves a project by name from the list of available projects.

        Args:
            name (str): The name of the project to retrieve.

        Returns:
            Dict[str, str]: The project data if found, otherwise an empty dictionary.
        """
        for project in self._projects:
            if project["name"] == name:
                return project["path"]
        return ""

    def set_globally_available_tags(self, tags: List[Dict[str, str]]) -> None:
        """
        Sets the list of globally available tags and notifies observers.

        Args:
            tags (List[Dict[str, str]]): List of globally available tag dictionaries.
        """
        self._globally_available_tags = tags
        self._update_locally_available_tags()
        self.notify_observers()

    def set_project_wizard_type(self, wizard_type: ProjectWizardType) -> None:
        """
        Sets the type of the project wizard (NEW or EDIT) .

        Args:
            wizard_type (ProjectWizardType): The type of the project wizard.
        """
        self._project_wizard_type = wizard_type

    def get_project_wizard_type(self) -> ProjectWizardType:
        """
        Retrieves the current type of the project wizard.

        Returns:
            ProjectWizardType: The current project wizard type.
        """
        return self._project_wizard_type

    def reset(self) -> None:
        """
        Resets the model to its default state and notifies observers.
        """
        self._set_defaults()
