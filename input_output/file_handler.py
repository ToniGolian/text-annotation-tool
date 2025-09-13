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

    def read_database_dict(self, tag_type: str) -> Dict:
        """
        Loads the database dictionary for a given tag_type.

        If the file does not exist, it will be generated using the CSV converter.

        Args:
            tag_type (str): The type of tag for which to load the database dictionary.

        Returns:
            Dict: The loaded or generated database dictionary.

        Raises:
            ValueError: If the tag_type is not configured or if required files are missing.

        Note:
            This method relies on the project settings and registry lock files to determine
            the correct database file to read. If no current database exists, a new one is created.
        """
        project_settings = self.read_file("project_settings")
        registry_lock_file_name = project_settings.get(
            "tags", {}).get(tag_type, {}).get("database", {}).get("registry_lock", "")
        if not registry_lock_file_name:
            raise ValueError(
                f"No registry lock file configured for tag type: {tag_type}")
        registry_lock_path = self._load_path(
            "project_databases_registry_locks", registry_lock_file_name)
        registry_lock = self.read_file(registry_lock_path)
        if not registry_lock:
            raise ValueError(
                f"Registry lock file is empty or missing: {registry_lock_file_name}")

        registry_name = registry_lock.get("database_registry", "")
        registry_path = self._load_path(
            "app_database_registries", registry_name)

        # if no dbs exist, create the first one
        is_new_database_needed = (registry_lock.get("count", 0) < 1
                                  or not registry_lock.get("current_db", "")
                                  or not os.path.exists(self._load_path(
                                      registry_path, registry_lock.get("current_db", "unknown_db"))))
        if is_new_database_needed:
            return self._create_new_database(registry_lock_path)

        database_file_name = registry_lock.get("current_db")

        database_file_path = self._load_path(
            registry_path, database_file_name)

        return self.read_file(database_file_path)

    def _create_new_database(self, registry_lock_path: str) -> Dict:
        """
        Creates a new database file based on the provided registry lock file path.
        Args:
            registry_lock_path (str): The path to the registry lock file.

        Returns:
            Dict: The created database dictionary.

        Note:
            This method modifies the registry lock file to update the current database information.
        """
        registry_lock = self.read_file(registry_lock_path)
        registry_name = registry_lock.get("database_registry", "")
        registry_path = self._load_path(
            "app_database_registries", registry_name)
        database_data = self._csv_db_converter.create_dict(registry_lock)
        version = registry_lock.get("count", 0)+1
        database_file_name = f"{registry_lock.get('name', '')}_v{version:04d}.json"
        database_file_path = self._load_path(
            registry_path, database_file_name)
        self.write_file(database_file_path, database_data)
        registry_lock["current_db"] = database_file_name
        registry_lock["dbs"].append(database_file_name)
        registry_lock["count"] = version
        self.write_file(key=registry_lock_path, data=registry_lock)
        return database_data

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

    def does_path_exist(self, file_path: str) -> bool:
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
        shutil.copy2(source_path, target_path)

    # context methods for project switching
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

    def get_current_project(self) -> str:
        """
        Retrieves the name of the current project context.

        Returns:
            str: The name of the current project, or None if no project is set.
        """
        return self._current_project
