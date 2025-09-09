import inspect
import os
import shutil
from typing import Dict
from input_output.interfaces import IReadWriteStrategy
from input_output.file_handler_strategies import JsonReadWriteStrategy, CsvReadWriteStrategy, TxtReadWriteStrategy
from utils.csv_db_converter import CSVDBConverter
from utils.path_manager import PathManager


class FileHandler:
    """
    Handler for reading and writing files with different formats based on file extension.

    All file paths are resolved via a central mechanism, which optionally includes
    dynamic project-aware substitution using a PathManager.
    """

    def __init__(self, encoding: str = 'utf-8', path_manager: PathManager = None) -> None:
        """
        Initializes FileHandler with an optional default encoding and sets up strategies.

        Args:
            encoding (str): The default file encoding to use for all strategies. Default is 'utf-8'.
            path_manager (PathManager, optional): If provided, this component is used to resolve dynamic paths.
        """
        self.encoding = encoding
        self._path_manager = path_manager
        self._strategies = {
            '.json': JsonReadWriteStrategy(encoding=self.encoding),
            '.csv': CsvReadWriteStrategy(encoding=self.encoding),
            '.txt': TxtReadWriteStrategy(encoding=self.encoding)
        }
        self._csv_db_converter = CSVDBConverter(self)
        self._current_project: str = None

    def _get_strategy(self, file_extension: str) -> IReadWriteStrategy:
        """
        Selects the appropriate strategy based on file extension.

        Args:
            file_extension (str): The file extension, including the leading dot.

        Returns:
            IReadWriteStrategy: The strategy instance for the given file extension.

        Raises:
            ValueError: If no strategy exists for the given file extension.
        """
        strategy = self._strategies.get(file_extension)
        if not strategy:
            raise ValueError(
                f"No strategy found for file extension: {file_extension}")
        return strategy

    def read_file(self, file_path: str, extension: str = "") -> Dict:
        """
        Reads a file using the appropriate strategy based on file extension.

        Args:
            file_path (str): Path to the file to be read or a key into the path configuration.
            extension (str, optional): Optional extension to append before reading.

        Returns:
            Dict: The content of the file as a dictionary.
        """
        file_path = self._load_path(file_path, extension)
        file_extension = os.path.splitext(file_path)[1]
        strategy = self._get_strategy(file_extension)
        return strategy.read(file_path)

    def write_file(self, key: str, data: Dict, extension: str = "") -> None:
        """
        Writes data to a file using the appropriate strategy based on file extension.

        Args:
            key (str): Path to the file or key to be resolved.
            data (Dict): Data to write to the file.
            extension (str, optional): Optional extension to append before writing.
        """
        file_path = self._load_path(key, extension)
        file_extension = os.path.splitext(file_path)[1]
        strategy = self._get_strategy(file_extension)
        strategy.write(file_path, data)

    def read_db_dict(self, tag_type: str) -> Dict:
        """
        Loads the database dictionary for a given tag_type.

        If the file does not exist, it will be generated using the CSV converter.

        Args:
            tag_type (str): The type of tag for which to load the database dictionary.

        Returns:
            Dict: The loaded or generated database dictionary.
        """
        tag_type = tag_type.lower()
        file_key = "project_db_dictionaries_folder"
        file_name = f"{tag_type}_db_dict.json"
        path = self._load_path(file_key, file_name)

        if not os.path.exists(path):
            db_data = self._csv_db_converter.create_dict(tag_type)
            self.write_file(file_key, db_data, file_name)
            return db_data

        return self.read_file(file_key, file_name)

    def _load_path(self, file_path: str, extension: str = "") -> str:
        """
        Resolves and constructs a file path using the PathManager.

        All resolution is delegated to the PathManager. If no PathManager is configured,
        an exception is raised.

        Args:
            file_path (str): The key or raw path to be resolved.
            extension (str, optional): Optional extension to append.

        Returns:
            str: Fully resolved and system-specific path.

        Raises:
            RuntimeError: If no PathManager is available.
        """
        if not self._path_manager:
            raise RuntimeError(
                "PathManager is required for path resolution but not set.")

        resolved_path = self._path_manager.resolve_path(file_path)

        if extension:
            resolved_path = os.path.join(resolved_path, extension)

        return self._convert_path_to_os_specific(resolved_path)

    def _convert_path_to_os_specific(self, path: str) -> str:
        """
        Converts a given path to a system-specific format.

        Args:
            path (str): The original path.

        Returns:
            str: System-normalized path.
        """
        return os.path.normpath(path)

    def resolve_path(self, key: str, extension: str = "") -> str:
        """
        Resolves a configuration key to a full file path, optionally appending an extension.
        Args:
            key (str): Key from config or already-resolved file path.
            extension (str, optional): Optional extension to append.
        Returns:
            str: Fully resolved and normalized file path.
        """
        return self._load_path(key, extension)

    def derive_file_name(self, file_path: str) -> str:
        """
        Extracts the base name (without extension) from a given file path.

        Args:
            file_path (str): Full file path.

        Returns:
            str: File name without extension.
        """
        return os.path.splitext(os.path.basename(file_path))[0]

    def create_directory(self, dir_path: str) -> None:
        """
        Creates a directory at the specified path, including any necessary parent directories.

        Args:
            dir_path (str): The directory path to create.
        """
        if os.path.exists(dir_path):
            raise FileExistsError(f"Directory already exists: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)

    def check_overwriting(self, file_path: str) -> bool:
        """
        Checks whether the given file path already exists.

        Args:
            file_path (str): The path to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        if os.path.exists(file_path):
            return True
        return False

    def copy_file(self, source_key: str, target_key: str, source_file_name: str = None, target_file_name: str = None, source_extension: str = "", target_extension: str = "") -> None:
        source_path = self.resolve_path(source_key, extension=source_extension)
        target_file_name = target_file_name if target_file_name else os.path.basename(
            source_path)
        target_path = self.resolve_path(
            target_key, extension=target_extension)
        if not target_extension:
            target_extension = os.path.splitext(source_path)[1]
            target_file_name = target_file_name + target_extension
            target_path = os.path.join(target_path, target_file_name)
        print(f"DEBUG {source_path=},\n {target_path=}")
        shutil.copy2(source_path, target_path)

    def change_context(self, project_name: str):
        """ Changes the current context to the specified project name. Updates paths accordingly.
        Args:
            project_name (str): The name of the project to switch context to.
        """
        self._current_project = project_name
        self._path_manager.update_paths(project_name)

    def use_project(self, project_name: str):
        """
        Context manager for temporarily switching the project.

        Args:
            project_name: The name of the project to switch into.
        """
        filehandler = self

        class _ProjectContext:
            def __enter__(self_inner) -> FileHandler:
                self_inner._prev = filehandler.get_current_project()
                filehandler.change_context(project_name)
                return filehandler

            def __exit__(self_inner, exc_type, exc_value, traceback) -> None:
                filehandler.change_context(self_inner._prev)

        return _ProjectContext()

    def test(self):
        print("FileHandler test")
        print(f"DEBUG {self._current_project=}")
