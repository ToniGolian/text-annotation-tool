from abc import ABC, abstractmethod
from typing import Dict


class ReadWriteStrategy(ABC):
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
