import os
from typing import Dict
from input_output.interfaces import IReadWriteStrategy
from input_output.file_handler_strategies import JsonReadWriteStrategy, CsvReadWriteStrategy, TxtReadWriteStrategy
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

    def write_file(self, file_path: str, data: Dict, extension: str = "") -> None:
        """
        Writes data to a file using the appropriate strategy based on file extension.

        Args:
            file_path (str): Path to the file or key to be resolved.
            data (Dict): Data to write to the file.
            extension (str, optional): Optional extension to append before writing.
        """
        file_path = self._load_path(file_path, extension)
        file_extension = os.path.splitext(file_path)[1]
        strategy = self._get_strategy(file_extension)
        strategy.write(file_path, data)

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
            print(f"DEBUG {extension=}")
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

    def get_default_path(self, key: str) -> str:
        """
        Retrieves the resolved and system-specific default path for a given configuration key.

        Args:
            key (str): Key in the application path configuration.

        Returns:
            str: Fully resolved default path.
        """
        return self._load_path(key)

    def derive_file_name(self, file_path: str) -> str:
        """
        Extracts the base name (without extension) from a given file path.

        Args:
            file_path (str): Full file path.

        Returns:
            str: File name without extension.
        """
        return os.path.splitext(os.path.basename(file_path))[0]
