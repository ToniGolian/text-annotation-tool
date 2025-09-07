import os
from input_output.interfaces import IFileHandler


class ProjectDirectoryManager:
    def create_project_structure(self, file_handler: IFileHandler, project_name: str) -> None:
        base_path = file_handler.resolve_path("project_folder")
        project_path = os.path.join(base_path, project_name)

        # config folder
        project_config_path = os.path.join(project_path, "config")
        color_schemes_path = os.path.join(project_config_path, "color_schemes")
        database_config_path = os.path.join(project_config_path, "database")
        groups_path = os.path.join(project_config_path, "groups")
        tags_path = os.path.join(project_path, "tags")

        # data folder
        project_data_path = os.path.join(project_path, "data")
        database_csv_path = os.path.join(project_data_path, "database_csv")
        database_dictionaries_path = os.path.join(
            project_data_path, "database_dictionaries")
