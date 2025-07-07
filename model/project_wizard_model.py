from typing import Dict, List
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
        self._projects: List[str] = []
        self._project_name: str = ""
        # List of {"name": str, "file_path": str}
        self._available_tags: List[Dict[str, str]] = []
        self._selected_tags: List[Dict[str, str]] = []
        self._tag_group_file_name: str = ""
        self._tag_groups: Dict[str, List[str]] = {}

    def set_state(self, state: dict) -> None:
        """
        Sets the internal state from a dictionary and notifies observers.

        Args:
            state (dict): Dictionary containing keys:
                'project_name', 'available_tags', 'selected_tags',
                'tag_group_file_name', 'tag_groups'
        """
        self._project_name = state.get("project_name", "")
        self._available_tags = state.get("available_tags", [])
        self._selected_tags = state.get("selected_tags", [])
        self._tag_group_file_name = state.get("tag_group_file_name", "")
        self._tag_groups = state.get("tag_groups", {})
        self.notify_observers()

    def get_state(self) -> dict:
        """
        Returns the current project configuration as a dictionary.

        Returns:
            dict: Dictionary of all project settings.
        """
        return {
            "projects": self._projects,
            "project_name": self._project_name,
            "available_tags": sorted([tag['display_name'] for tag in self._available_tags]),
            "selected_tags": sorted(self._selected_tags),
            "tag_group_file_name": self._tag_group_file_name,
            "tag_groups": self._tag_groups
        }

    def add_tag_group(self, group_name: str, tags: List[str]) -> None:
        """
        Adds a new tag group to the internal state and notifies observers.

        Args:
            group_name (str): Name of the tag group.
            tags (list[str]): List of tag names to associate with the group.
        """
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
                    "selected_tags": list[dict[str, str]],
                    "cleaned_selected_tags": list[dict[str, str]]
                }
        """
        cleaned_tags = [
            {
                "name": self._clean_name(tag["name"]),
                "file_path": tag["file_path"]
            }
            for tag in self._selected_tags
            if "name" in tag and "file_path" in tag
        ]

        return {
            "project_name": self._project_name,
            "tag_group_file_name": self._tag_group_file_name,
            "groups": self._tag_groups,
            "selected_tags": self._selected_tags,
            "cleaned_selected_tags": cleaned_tags
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

    def add_selected_tags(self, tags: List[Dict[str, str]]) -> None:
        """
        Adds the given tags to the selected tags list and notifies observers.

        Args:
            tags (list[Dict[str, str]]): List of tag dictionaries to add.
        """
        self._selected_tags.extend(tags)
        print(f"DEBUG model {self._selected_tags=}")
        self.notify_observers()

    def remove_selected_tags(self, selected_indices: List[int]) -> None:
        """
        Removes specified tags from the selected tags list by index and notifies observers.

        Args:
            selected_indices (List[int]): List of indices of tags to remove.
        """
        self._selected_tags = [
            tag for i, tag in enumerate(self._selected_tags) if i not in selected_indices
        ]
        self.notify_observers()

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
