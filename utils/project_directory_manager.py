import os
from typing import Dict
from input_output.interfaces import IFileHandler


class ProjectDirectoryManager:
    def __init__(self, file_handler: IFileHandler) -> None:
        self._file_handler = file_handler
        self._project_marker = "<project>"

    def create_project_structure(self, project_name: str) -> None:
        # paths = []
        project_template = self._file_handler.read_file("project_template")

        for directory_name, directory in project_template.items():
            base_path, target_directory = self._find_base(project_name=project_name,
                                                          directory_name=directory_name,
                                                          directory=directory)
            print(f"DEBUG base path für {directory_name=}: {base_path}")
            print(
                f"DEBUG target directory für {directory_name =}: {target_directory}\n\n")
            self._create_subdirectories(base_path, target_directory)

        # # app data
        # app_data_base_path = self._file_handler.resolve_path("project_folder")
        # project_app_data_path = os.path.join(app_data_base_path, project_name)
        # paths.append(project_app_data_path)

        # # config folder
        # project_config_path = os.path.join(project_app_data_path, "config")
        # color_schemes_path = os.path.join(project_config_path, "color_schemes")
        # database_config_path = os.path.join(project_config_path, "database")
        # groups_path = os.path.join(project_config_path, "groups")
        # tags_path = os.path.join(project_app_data_path, "tags")
        # paths.append(project_config_path)
        # paths.append(color_schemes_path)
        # paths.append(database_config_path)
        # paths.append(groups_path)
        # paths.append(tags_path)

        # # data folder
        # project_data_path = os.path.join(project_app_data_path, "databases")
        # database_csv_path = os.path.join(project_data_path, "csv")
        # database_dictionaries_path = os.path.join(
        #     project_data_path, "dictionaries")
        # paths.append(project_data_path)
        # paths.append(database_csv_path)
        # paths.append(database_dictionaries_path)

        # # project_data
        # data_path = self._file_handler.resolve_path("data_folder")
        # project_data_path = os.path.join(data_path, project_name)
        # annotation_path = os.path.join(project_data_path, "annotations")
        # comparison_path = os.path.join(project_data_path, "comparisons")
        # extractions_path = os.path.join(project_data_path, "extractions")
        # merged_documents_path = os.path.join(
        #     project_data_path, "merged_documents")
        # paths.append(project_data_path)
        # paths.append(annotation_path)
        # paths.append(comparison_path)
        # paths.append(extractions_path)
        # paths.append(merged_documents_path)

        # # create directories
        # for path in paths:
        #     self._file_handler.create_directory(path)

    def _find_base(self, project_name: str, directory_name: str, directory: Dict) -> str:
        """
        Find the base path and directory for a given directory name.
        Args:
            project_name (str): The name of the project.
            directory_name (str): The name of the directory to find.
            directory (Dict): The current directory structure.
        Returns:
            tuple: The base path and the target directory dictionary.
        """
        print(f"DEBUG Finding base: {directory_name=}")
        path, target_directory = self._dfs(
            directory_name, directory, self._project_marker)
        return path.replace(self._project_marker, project_name), target_directory.get("directories", {}).get(self._project_marker, {})

    def _dfs(self, directory_name: str, directory: Dict, target_key: str) -> str:
        """
        Depth-first search to find the base path for a given directory name.
        Args:
            directory_name (str): The name of the directory to find.
            directory (Dict): The current directory structure.
            target_key (str): The key to search for.
        Returns:
            tuple: The base path and the target directory dictionary.
        Raises:
            FileNotFoundError: If the target key is not found in the directory structure.
        """
        print(f"DEBUG dfs in {directory_name=}")
        if directory_name == target_key:
            return target_key, directory
        subdirectories = directory.get("directories", {})
        if not subdirectories:
            return "", directory
        for subdirectory_name, subdirectory in subdirectories.items():
            if target_key in subdirectory.get("directories", {}):
                return subdirectory_name, subdirectory
            else:
                subpath, target_directory = self._dfs(
                    directory_name=subdirectory_name, directory=subdirectory, target_key=target_key)
                return os.path.join(directory_name, subpath), target_directory

    def _create_subdirectories(self, base_path: str, directory: Dict) -> None:
        """
        Recursively create subdirectories based on the directory structure.
        Args:
            base_path (str): The base path where directories will be created.
            directory (Dict): The current directory structure.
        """
        subdirectories = directory.get("directories", {})
        for subdirectory_name, subdirectory in subdirectories.items():
            if not isinstance(subdirectory, dict):
                # Skip if it's not a dict (e.g. it's a list of files)
                continue
            new_path = os.path.join(base_path, subdirectory_name)
            # self._file_handler.create_directory(new_path)
            # todo reactivate later
            if subdirectory.get("directories", {}):
                self._create_subdirectories(
                    base_path=new_path, directory=subdirectory)
