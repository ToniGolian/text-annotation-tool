from observer.interfaces import IPublisher
from typing import Dict, List


class ConfigurationModel(IPublisher):
    """
    Manages application configuration, including layout, templates, and tag metadata.

    This model does not load any data during initialization. Instead, external components
    must supply the layout state and project path via `update_state`. From this input,
    template information and tag metadata such as ID prefixes and references are extracted.
    """

    def __init__(self) -> None:
        """
        Initializes an empty ConfigurationModel.

        All internal state is uninitialized until `update_state` is called.
        """
        super().__init__()

        self._project_path = ""
        self._color_path = ""
        # self._saved_layout = None
        self._layout = {}
        self._id_prefixes = {}
        self._id_names = {}
        self._id_ref_attributes = {}

    def set_configuration(self, configuration: Dict) -> None:
        """
        Updates the model state from a preassembled configuration dictionary.

        This method expects the complete configuration dictionary to be passed in,
        including the layout state, template definitions, tag metadata, and color scheme.

        Args:
            configuration (Dict): A dictionary containing all configuration components. Expected keys:
                                - "layout"
                                - "template_groups"
                                - "id_prefixes"
                                - "id_names"
                                - "id_ref_attributes"
                                - "color_scheme"
        """
        self._layout = configuration.get("layout", {})
        self._id_prefixes = configuration.get("id_prefixes", {})
        self._id_names = configuration.get("id_names", {})
        self._id_ref_attributes = configuration.get("id_ref_attributes", {})
        self._color_scheme = configuration.get("color_scheme", {})

        self.notify_observers()

    def get_state(self) -> Dict:
        """
        Returns the current UI and layout state.

        This includes all information passed in via `update_state`, such as
        window positions and template group definitions.

        Returns:
            Dict: The layout state dictionary.
        """
        return self._layout

    def get_color_scheme(self) -> Dict:
        """
        Loads and returns the color scheme for the current project.

        Returns:
            Dict: Dictionary of UI color settings.
        """
        return self._color_scheme

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
