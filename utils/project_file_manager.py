from typing import Any, Dict
from controller.interfaces import IController
from input_output.interfaces import IFileHandler


class ProjectFileManager:
    def __init__(self, controller: IController, file_handler: IFileHandler):
        self._file_handler = file_handler
        self._controller = controller

        self._project_data = {}

    def create_project_files(self, project_name: str, project_data: Dict[str, Any]):
        with self._file_handler.use_project(project_name):
            self._project_data = project_data
            self._create_tag_files()
            self._create_tag_group_file()
            self._create_database_config_files()
            self._create_default_color_file()
            self._create_project_settings_files()
            self._create_csv_database_files()
            self._create_database_dictionary_files()

    def _create_tag_files(self):
        """
        Creates tag files for the given tags.
        Args:
            tags (List[Dict[str, str]]): List of tags to create files for in the current project.
        Returns:
            List[Dict[str, str]]: List of tags with updated unique tag names.
        """
        tags = self._project_data.get("selected_tags", [])

        for tag in tags:
            self._file_handler.copy_file(
                source_key=tag["path"], target_key="project_tags_folder", target_file_name=tag["name"].lower())
            tag_file_content = self._file_handler.read_file(
                "project_tags_folder", f"{tag['name']}.json")
            tag_file_content['type'] = tag['name']
            self._file_handler.write_file(
                key="project_tags_folder", data=tag_file_content, extension=f"{tag['name']}.json")

    def _create_tag_group_file(self) -> None:
        """
        Creates a tag group file based on the provided project data.
        Args:
            project_data (Dict[str, Any]): The project data containing tag group information.
        """
        tags = self.project_data.get("selected_tags", [])
        tag_group_file_name = self.project_data.get("tag_group_file_name", "")
        tag_groups = self.project_data.get("tag_groups", {})
        tag_groups = {group_name: [tag["name"] for tag in tags if tag["display_name"]
                                   in tag_display_names] for group_name, tag_display_names in tag_groups.items()}

        tag_group_file_name = f"{tag_group_file_name}.json"
        self._file_handler.write_file(
            key="project_groups", data=tag_groups, extension=tag_group_file_name)

    def _create_database_config_files(self) -> None:
        pass

    def _create_default_color_file(self) -> None:
        pass

    def _create_project_settings_files(self) -> None:
        pass

    def _create_csv_database_files(self) -> None:
        pass

    def _create_database_dictionary_files(self) -> None:
        pass
