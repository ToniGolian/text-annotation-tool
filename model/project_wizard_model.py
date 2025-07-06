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
        self._project_name: str = ""
        self._available_tags: list[str] = []
        self._selected_tags: list[str] = []
        self._tag_group_file_name: str = ""
        self._tag_groups: dict[str, list[str]] = {}

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
            "project_name": self._project_name,
            "available_tags": self._available_tags,
            "selected_tags": self._selected_tags,
            "tag_group_file_name": self._tag_group_file_name,
            "tag_groups": self._tag_groups
        }

    def add_tag_group(self, group_name: str, tags: list[str]) -> None:
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
