from typing import Dict
from input_output.file_handler import FileHandler
from input_output.template_loader import TemplateLoader


class ConfigurationManager:
    """
    Loads and prepares the full configuration using keys defined in the application path configuration.

    This manager uses the FileHandler to resolve and load files related to layout, project templates,
    and color scheme.
    """

    def __init__(self, file_handler: FileHandler) -> None:
        """
        Initializes the ConfigurationManager with a FileHandler instance.

        Args:
            file_handler (FileHandler): Used to load configuration files via key-based paths.
        """
        self._file_handler = file_handler
        self._template_loader = TemplateLoader(file_handler=file_handler)

    def load_configuration(self) -> Dict:
        """
        Loads layout state, color scheme, and associated template group configuration.

        The layout file is expected to include a `project` field, used to
        derive template and attribute mapping based on that project context.

        Returns:
            Dict: A dictionary containing full layout state including template groups,
                  ID prefixes, ID attributes, ID references, and color scheme.
        """
        layout = {}
        project_settings = self._file_handler.read_file("project_settings")
        color_scheme_file_name = project_settings.get("color_scheme") + ".json"
        color_scheme = self._file_handler.read_file(
            "project_color_scheme_folder", color_scheme_file_name)

        project_path = self._file_handler.resolve_path(
            "project_config")
        template_groups = self._template_loader.load_template_groups(
            project_path)

        id_prefixes = {}
        id_names = {}
        id_ref_attributes = {}
        tag_types = []

        for group in template_groups:
            for template in group.get("templates", []):
                tag_type = template.get("type")
                tag_types.append(tag_type)
                attributes = template.get("attributes", {})

                id_prefixes[tag_type] = template.get("id_prefix", "")
                id_names[tag_type] = next(
                    (attr for attr, details in attributes.items()
                     if details.get("type") == "ID"), ""
                )
                id_ref_attributes[tag_type] = [
                    attr for attr, details in attributes.items()
                    if details.get("type") in {"ID", "IDREF"}
                ]

        layout["template_groups"] = template_groups
        layout["tag_types"] = tag_types
        return {
            "layout": layout,
            "id_prefixes": id_prefixes,
            "id_names": id_names,
            "id_ref_attributes": id_ref_attributes,
            "color_scheme": color_scheme
        }
