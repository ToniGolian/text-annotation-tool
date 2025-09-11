from typing import Any, Dict
from controller.interfaces import IController
from input_output.interfaces import IFileHandler


class ProjectFileManager:
    def __init__(self, controller: IController, file_handler: IFileHandler):
        self._file_handler = file_handler
        self._controller = controller

        self._project_file_information = {}

    def create_project_files(self, project_name: str, project_file_information: Dict[str, Any]):
        with self._file_handler.use_project(project_name):
            self._project_file_information = project_file_information
            print(f"DEBUG {self._project_file_information=}")
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
            # todo how to move this to the normalization step?
            tag_file_content = self._file_handler.read_file(
                "project_tags_folder", f"{tag['name']}.json")
            tag_file_content['type'] = tag['name']
            # todo end
            self._file_handler.write_file(
                key="project_tags_folder", data=tag_file_content, extension=f"{tag['name']}.json")

    def _create_tag_group_file(self) -> None:
        """
        Creates a tag group file based on the provided project data.
        Args:
            project_data (Dict[str, Any]): The project data containing tag group information.
        """
        tag_groups = self.project_data.get("tag_groups", {})
        tag_group_file_name = self.project_data.get("tag_group_file_name", "")
        tag_group_file_name = f"{tag_group_file_name}.json"
        self._file_handler.write_file(
            key="project_groups", data=tag_groups, extension=tag_group_file_name)

    def _create_database_config_files(self) -> None:
        raise NotImplementedError(
            "_create_database_config_files method not implemented yet.")

    def _create_default_color_file(self) -> None:
        raise NotImplementedError(
            "_create_default_color_file method not implemented yet.")

    def _create_project_settings_files(self) -> None:
        raise NotImplementedError(
            "_create_project_settings_files method not implemented yet.")

    def _create_csv_database_files(self) -> None:
        raise NotImplementedError(
            "_create_csv_database_files method not implemented yet.")

    def _create_database_dictionary_files(self) -> None:
        raise NotImplementedError(
            "_create_database_dictionary_files method not implemented yet.")
