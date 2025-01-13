from abc import ABC, abstractmethod
from typing import Dict


class IFileHandler(ABC):
    """Interface for a file handler supporting reading and writing files based on file extensions."""

    @abstractmethod
    def read_file(self, file_path: str) -> Dict:
        """
        Reads a file using the appropriate strategy based on file extension.

        Args:
            file_path (str): Path to the file to be read.

        Returns:
            Dict: The content of the file as a dictionary.
        """
        pass

    @abstractmethod
    def write_file(self, file_path: str, data: Dict) -> None:
        """
        Writes data to a file using the appropriate strategy based on file extension.

        Args:
            file_path (str): Path to the file to be written.
            data (Dict): Data to be written to the file.
        """
        pass

    @abstractmethod
    def _convert_path_to_os_specific(self, path: str) -> str:
        """
        Converts a given path to a system-specific format.

        Args:
            path (str): The original path in a neutral format (e.g., "folder/folder/filename.filetype").

        Returns:
            str: The path converted to the system-specific format.
        """
        pass


class IProcessorStrategy(ABC):
    """Interface for processing raw data into a structured format."""

    def __init__(self, data: Dict) -> None:
        """
        Initializes the processor with raw data.

        Args:
            data (Dict): Raw data to be processed.
        """
        self.data = data

    @abstractmethod
    def process(self) -> Dict:
        """
        Processes the raw data into a structured format.
                Returns:
            Dict: A dictionary with structured, processed data.
        """
        pass


class IReadWriteStrategy(ABC):
    """Interface for reading and writing files with a specific format."""

    @abstractmethod
    def read(self, file_path: str) -> Dict:
        """
        Reads the file and returns its content.

        Args:
            file_path (str): Path to the file.

        Returns:
            Dict: Parsed file content.
        """
        pass

    @abstractmethod
    def write(self, file_path: str, data: Dict) -> None:
        """
        Writes data to the file.

        Args:
            file_path (str): Path to the file.
            data (Dict): Data to be written.
        """
        pass


class ITemplateLoader(ABC):
    @abstractmethod
    def load_template_groups(self, project_path: str):
        pass
