import os
from typing import List, Dict
from input_output.file_handler import FileHandler
from input_output.interfaces import ITemplateLoader


class TemplateLoader(ITemplateLoader):
    """
    Manages loading and storing of tag templates from JSON files.

    Attributes:
        _file_handler (FileHandler): Instance of FileHandler to manage file operations.
    """

    def __init__(self) -> None:
        """
        Initializes the TemplateLoader and creates an instance of FileHandler.
        """
        self._file_handler: FileHandler = FileHandler()

    def load_template_groups(self, project_path: str) -> List[Dict[str, List[Dict]]]:
        """
        Loads template groups and their associated tag templates from a project directory.

        This method reads a `groups.json` file located in the given `project_path`
        and retrieves all group members. For each group member, it loads a JSON file
        containing tag templates from the `tags` subdirectory.

        Args:
            project_path (str): The path to the project directory where `groups.json` 
                                and the `tags/` subdirectory are located.

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
        project_path = os.path.join(project_path, "groups.json")
        groups: Dict[str, List[str]
                     ] = self._file_handler.read_file(project_path)
        template_groups: List[Dict[str, List[Dict]]] = []

        for group_name, group_members in groups.items():
            templates: List[Dict] = []
            for group_member in group_members:
                file_path = os.path.join(
                    os.path.dirname(project_path),
                    f"tags/{group_member.lower()}.json"
                )
                templates.append(
                    self._file_handler.read_file(file_path=file_path))
            template_groups.append(
                {"group_name": group_name, "templates": templates})

        return template_groups
