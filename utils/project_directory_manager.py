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
            self._create_subdirectories(base_path, target_directory)

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
        path, target_directory = self._dfs(
            directory_name, directory, self._project_marker)
        return path.replace(self._project_marker, project_name), target_directory

    def _dfs(self, directory_name: str, directory: Dict, target_key: str) -> str:
        """
        Depth-first search to find the base path for a given directory name.
        Args:
            directory_name (str): The name of the directory to find.
            directory (Dict): The current directory structure.
            target_key (str): The key to search for.
        Returns:
            tuple: The base path and the target directory dictionary.
        Notes:
            We assume that there is only one directory named `target_key` in the entire structure.
            Otherwise, the function may return an arbitrary occurrence.
        Raises:
            FileNotFoundError: If the target key is not found in the directory structure.
        """
        target_path = ""
        target_directory = None

        # target found
        if directory_name == target_key:
            return target_key, directory
        subdirectories = directory.get("directories", {})
        # entered a leaf
        if not subdirectories:
            return "", None
        # explore subdirectories recursively
        for subdirectory_name, subdirectory in subdirectories.items():
            subpath, target_directory = self._dfs(
                directory_name=subdirectory_name, directory=subdirectory, target_key=target_key)
            if subpath:
                target_path = os.path.join(directory_name, subpath)
                break  # Stop searching after the first match
        return target_path, target_directory

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
            self._file_handler.create_directory(new_path)
            if subdirectory.get("directories", {}):
                self._create_subdirectories(
                    base_path=new_path, directory=subdirectory)
