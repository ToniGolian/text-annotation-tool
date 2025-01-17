import os
from typing import Dict, Type
from input_output.interfaces import IReadWriteStrategy
from input_output.file_handler_strategies import JsonReadWriteStrategy, CsvReadWriteStrategy, TxtReadWriteStrategy


class FileHandler:
    """Handler for reading and writing files with different formats based on file extension."""

    def __init__(self, encoding: str = 'utf-8') -> None:
        """
        Initializes FileHandler with an optional default encoding and sets up strategies.

        Args:
            encoding (str): The default file encoding to use for all strategies. Default is 'utf-8'.
        """
        self._app_paths_file = "app_data/app_paths.json"
        self.encoding = encoding
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
            ReadWriteStrategy: The strategy instance for the given file extension.

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
            file_path (str): Path to the file to be read.

        Returns:
            Dict: The content of the file as a dictionary.
        """
        file_path = self._load_path(file_path, extension)
        print(f"{file_path=}")
        file_extension = f".{file_path.split('.')[-1]}"
        strategy = self._get_strategy(file_extension)
        return strategy.read(file_path)

    def write_file(self, file_path: str, data: Dict, extension: str = "") -> None:
        """
        Writes data to a file using the appropriate strategy based on file extension.

        Args:
            file_path (str): Path to the file to be written.
            data (Dict): Data to be written to the file.
        """
        # Attempt to load file_path from the app paths file
        app_paths = self._get_strategy('.json').read(self._app_paths_file)
        file_path = app_paths.get(file_path, file_path)

        file_path = self._load_path(file_path, extension)
        file_extension = f".{file_path.split('.')[-1]}"
        strategy = self._get_strategy(file_extension)
        strategy.write(file_path, data)

    def _load_path(self, file_path: str, extension: str) -> str:
        app_paths = self._get_strategy('.json').read(self._app_paths_file)
        file_path = app_paths.get(file_path, file_path)
        file_path += extension
        return self._convert_path_to_os_specific(file_path)

    def _convert_path_to_os_specific(self, path: str) -> str:
        """
        Converts a given path to a system-specific format.

        Args:
            path (str): The original path in a neutral format (e.g., "folder/folder/filename.filetype").

        Returns:
            str: The path converted to the system-specific format.
        """
        return os.path.normpath(path)
