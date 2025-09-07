import os
from input_output.interfaces import IFileHandler


class ProjectDirectoryManager:
    def __init__(self, file_handler: IFileHandler) -> None:
        self._file_handler = file_handler

    def create_project_structure(self, project_name: str) -> None:
        paths = []
        # app data
        app_data_base_path = self._file_handler.resolve_path("project_folder")
        project_app_data_path = os.path.join(app_data_base_path, project_name)
        paths.append(project_app_data_path)

        # config folder
        project_config_path = os.path.join(project_app_data_path, "config")
        color_schemes_path = os.path.join(project_config_path, "color_schemes")
        database_config_path = os.path.join(project_config_path, "database")
        groups_path = os.path.join(project_config_path, "groups")
        tags_path = os.path.join(project_app_data_path, "tags")
        paths.append(project_config_path)
        paths.append(color_schemes_path)
        paths.append(database_config_path)
        paths.append(groups_path)
        paths.append(tags_path)

        # data folder
        project_data_path = os.path.join(project_app_data_path, "databases")
        database_csv_path = os.path.join(project_data_path, "csv")
        database_dictionaries_path = os.path.join(
            project_data_path, "dictionaries")
        paths.append(project_data_path)
        paths.append(database_csv_path)
        paths.append(database_dictionaries_path)

        # project_data
        data_path = self._file_handler.resolve_path("data_folder")
        project_data_path = os.path.join(data_path, project_name)
        annotation_path = os.path.join(project_data_path, "annotations")
        comparison_path = os.path.join(project_data_path, "comparisons")
        extractions_path = os.path.join(project_data_path, "extractions")
        merged_documents_path = os.path.join(
            project_data_path, "merged_documents")
        paths.append(project_data_path)
        paths.append(annotation_path)
        paths.append(comparison_path)
        paths.append(extractions_path)
        paths.append(merged_documents_path)

        # create directories
        for path in paths:
            self._file_handler.create_directory(path)
