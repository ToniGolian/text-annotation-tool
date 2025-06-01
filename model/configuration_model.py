from observer.interfaces import IPublisher
from input_output.template_loader import TemplateLoader
from input_output.file_handler import FileHandler
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

        self._template_loader = TemplateLoader()
        self._filehandler = FileHandler()

        self._project_path = ""
        self._color_path = ""
        self._saved_layout = None
        self._layout_state = {}
        self._id_prefixes = {}
        self._id_names = {}
        self._id_ref_attributes = {}

    def update_state(self, layout_state: dict, project_path: str) -> None:
        """
        Updates the configuration based on layout and project context.

        This method loads template definitions, extracts tag type metadata (ID prefixes,
        ID attributes, and ID references), and sets up internal state to reflect the current
        UI and project structure.

        Args:
            layout_state (dict): The layout state loaded from external configuration.
            project_path (str): Path to the project configuration root directory.
        """
        self._layout_state = layout_state
        self._saved_layout = layout_state
        self._project_path = project_path
        self._color_path = project_path + "color_scheme.json"

        self._filehandler.read_file(self._color_path)
        self._layout_state["template_groups"] = self._template_loader.load_template_groups(
            project_path)

        for group in self._layout_state["template_groups"]:
            for template in group.get("templates", []):
                tag_type = template.get("type")
                attributes = template.get("attributes", {})

                self._id_prefixes[tag_type] = template.get("id_prefix", "")
                self._id_names[tag_type] = next(
                    (attr for attr, details in attributes.items()
                     if details.get("type") == "ID"),
                    ""
                )
                self._id_ref_attributes[tag_type] = [
                    attr for attr, details in attributes.items()
                    if details.get("type") in {"ID", "IDREF"}
                ]

        self.notify_observers()

    def get_state(self) -> Dict:
        """
        Returns the current UI and layout state.

        This includes all information passed in via `update_state`, such as
        window positions and template group definitions.

        Returns:
            Dict: The layout state dictionary.
        """
        return self._layout_state

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
        for group in self._layout_state["template_groups"]:
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
