import os
from typing import Dict, List
from input_output.file_handler import FileHandler


class ProjectConfigurationManager:
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

        template_groups = self._load_template_groups()

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
        }

    def _load_template_groups(self) -> List[Dict[str, List[Dict]]]:
        """
        Loads template groups and their associated tag templates from a project directory.

        This method reads a `groups.json` file located in the given `project_path`
        and retrieves all group members. For each group member, it loads a JSON file
        containing tag templates from the `tags` subdirectory.

        Returns:
            List[Dict[str, List[Dict]]]: A list of dictionaries, where each dictionary represents a group.
                                         Each dictionary contains:
                                         - `group_name`: The name of the group (str).
                                         - `templates`: A list of tag template dictionaries for the group members (List[Dict]).

        Example Output:
            [
                {
                    "group_name": "GroupA",
                    "templates": [
                        { ... },  # Data loaded from tags/member1.json
                        { ... }   # Data loaded from tags/member2.json
                    ]
                },
                {
                    "group_name": "GroupB",
                    "templates": [
                        { ... }    # Data loaded from tags/member3.json
                    ]
                }
            ]

        Raises:
            FileNotFoundError: If `groups.json` or a tag template file is not found.
            JSONDecodeError: If a file is not in valid JSON format.
        """
        project_data = self._file_handler.read_file("project_settings")
        group_file_name = project_data.get(
            "current_group_file", "default_groups")

        groups: Dict[str, List[str]
                     ] = self._file_handler.read_file("project_tag_groups_directory", group_file_name)
        template_groups: List[Dict[str, List[Dict]]] = []

        for group_name, group_members in groups.items():
            templates: List[Dict] = []
            for group_member in group_members:
                file_path = os.path.join(self._file_handler.resolve_path(
                    "project_config_directory"),
                    f"tags/{group_member.lower()}.json"
                )
                templates.append(
                    self._file_handler.read_file(file_path=file_path))
            template_groups.append(
                {"group_name": group_name, "templates": templates})

        return template_groups

    def get_projects(self) -> List[Dict[str, str]]:
        """
        Scans the project directory for valid projects and returns their names and config file paths.

        Uses the FileHandler to read project.json files in each subdirectory of the project path.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing:
                - 'name': Project name from project.json
                - 'path': Absolute path to the project's project.json file

        Raises:
            FileNotFoundError: If a project.json file is missing in a subdirectory.
            JSONDecodeError: If a project.json is not a valid JSON file.
        """
        projects_path = self._file_handler.resolve_path("project_directory")
        results: List[Dict[str, str]] = []

        for directory in os.listdir(projects_path):
            subdir_path = os.path.join(projects_path, directory)
            if os.path.isdir(subdir_path):
                project_file = os.path.join(
                    subdir_path, "config", "settings", "project.json")  # hardcoded since the filehandler would need project context
                if os.path.isfile(project_file):
                    data = self._file_handler.read_file(file_path=project_file)
                    project_name = data.get("name")
                    if project_name:
                        results.append({
                            "name": project_name,
                            "path": project_file
                        })

        return results

    # todo move to another class
    def get_available_tags(self) -> List[Dict[str, str]]:
        """
        Scans all project directories and collects tag definitions.

        For each tag file found in the `tags` subdirectory of a project, returns a dictionary with:
            - 'name': Name of the tag (derived from file name, without extension)
            - 'path': Absolute path to the tag file
            - 'project': Name of the project (from project.json)

        Returns:
            List[Dict[str, str]]: List of all tag definitions across all projects.

        Raises:
            FileNotFoundError: If a required file or directory is missing.
            JSONDecodeError: If project.json is invalid.
        """
        projects_path = self._file_handler.resolve_path("project_directory")
        results: List[Dict[str, str]] = []
        for directory in os.listdir(projects_path):
            subdir_path = os.path.join(projects_path, directory)
            if os.path.isdir(subdir_path):
                project_file = os.path.join(
                    subdir_path, "config", "settings", "project.json")
                tags_dir = os.path.join(subdir_path, "config", "tags")
                if not os.path.isfile(project_file) or not os.path.isdir(tags_dir):
                    continue

                project_data = self._file_handler.read_file(
                    file_path=project_file)
                project_name = project_data.get("name")
                if not project_name:
                    continue

                for file_name in os.listdir(tags_dir):
                    if file_name.endswith(".json"):
                        tag_name = os.path.splitext(file_name)[0]
                        tag_path = os.path.join(tags_dir, file_name)
                        has_database = self._file_handler.read_file(
                            file_path=tag_path).get("has_database", False)
                        results.append({
                            "name": tag_name.upper(),
                            "path": tag_path,
                            "project": project_name,
                            "has_database": has_database
                        })
        return results
