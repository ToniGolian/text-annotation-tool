from abc import ABC, abstractmethod
from typing import Dict


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
    pass
