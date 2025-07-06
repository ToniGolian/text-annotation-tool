from observer.interfaces import IPublisher
from typing import Dict, List


class LayoutConfigurationModel(IPublisher):
    """
    Manages application configuration, including layout, templates, and tag metadata.

    This model does not load any data during initialization. Instead, external components
    must supply the layout state and project path via `update_state`. From this input,
    template information and tag metadata such as ID prefixes and references are extracted.
    """

    def __init__(self) -> None:
        """
        Initializes an empty LayoutConfigurationModel.

        All internal state is uninitialized until `update_state` is called.
        """
        super().__init__()

        self._layout = {}
        self._id_prefixes = {}
        self._id_names = {}
        self._id_ref_attributes = {}

    def set_configuration(self, configuration: Dict) -> None:
        """
        Updates the model state from a preassembled configuration dictionary.

        This method expects the complete configuration dictionary to be passed in,
        including the layout state, template definitions, tag metadata, color scheme,
        and search normalization.

        Args:
            configuration (Dict): A dictionary containing all configuration components. Expected keys:
                                - "layout"
                                - "id_prefixes"
                                - "id_names"
                                - "id_ref_attributes"
        """
        self._layout = configuration.get("layout", {})
        self._id_prefixes = configuration.get("id_prefixes", {})
        self._id_names = configuration.get("id_names", {})
        self._id_ref_attributes = configuration.get("id_ref_attributes", {})
        self.notify_observers()

    def get_tag_types(self) -> List[str]:
        """
        Returns all tag types defined in the template groups.

        Returns:
            List[str]: A list of tag type strings.
        """
        tag_types = []
        for group in self._layout["template_groups"]:
            for template in group.get("templates", []):
                tag_types.append(template.get("type", ""))
        return tag_types

    def get_id_prefixes(self) -> Dict[str, str]:
        """
        Returns a mapping of tag types to their ID prefixes.

        Returns:
            Dict[str, str]: Dictionary mapping tag type to ID prefix.
        """
        return self._id_prefixes

    def get_id_name(self, tag_type: str) -> str:
        """
        Returns the attribute name used as ID for a given tag type.

        Args:
            tag_type (str): The tag type to query.

        Returns:
            str: The ID attribute name, or an empty string if not defined.
        """
        return self._id_names.get(tag_type, "")

    def get_id_refs(self, tag_type: str) -> List[str]:
        """
        Returns all attributes of a tag type that reference IDs.

        Args:
            tag_type (str): The tag type to query.

        Returns:
            List[str]: List of attribute names that are ID or IDREF types.
        """
        return self._id_ref_attributes.get(tag_type, [])

    def get_num_comparison_displays(self) -> int:
        """
        Retrieves the number of comparison displays.

        Returns:
            int: The number of comparison displays.
        """
        return self._layout["num_comparison_displays"]

    def set_num_comparison_displays(self, num_comparison_displays: int) -> None:
        """
        Sets the number of dynamically created comparison displays.

        Args:
            num_comparison_displays (int): The number of comparison displays.
        """
        self._layout["num_comparison_displays"] = num_comparison_displays
        self.notify_observers()

    def get_active_notebook_index(self) -> int:
        """
        Retrieves the index of the currently active notebook tab.

        Returns:
            int: The index of the active notebook tab.
        """
        return self._layout["active_notebook_index"]

    def set_active_notebook_index(self, index: int) -> None:
        """
        Sets the index of the currently active notebook tab.

        Args:
            index (int): The index to set as active.
        """
        self._layout["active_notebook_index"] = index
        self.notify_observers()

    def get_state(self) -> dict:
        """
        Retrieves the current state of the appearance model.

        Returns:
            dict: A dictionary containing:
                - "layout" (dict): The current layout configuration.
                - "num_comparison_displays" (int): The number of dynamically created comparison displays.
                - "active_notebook_index" (int): The index of the currently active notebook tab.
        """
        return self._layout
