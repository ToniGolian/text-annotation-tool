import json
import csv
from typing import Dict
from input_output.interfaces import IReadWriteStrategy


class JsonReadWriteStrategy(IReadWriteStrategy):
    """Strategy for reading and writing JSON files."""

    def __init__(self, encoding: str = 'utf-8') -> None:
        """
        Initializes JsonReadWriteStrategy with an optional encoding.

        Args:
            encoding (str): The file encoding to use. Default is 'utf-8'.
        """
        self.encoding = encoding

    def read(self, file_path: str) -> Dict:
        with open(file_path, 'r', encoding=self.encoding) as file:
            return json.load(file)

    def write(self, file_path: str, data: Dict) -> bool:
        try:
            with open(file_path, 'w', encoding=self.encoding) as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False


class CsvReadWriteStrategy(IReadWriteStrategy):
    """Strategy for reading and writing CSV files."""

    def __init__(self, encoding: str = 'utf-8') -> None:
        """
        Initializes CsvReadWriteStrategy with an optional encoding.

        Args:
            encoding (str): The file encoding to use. Default is 'utf-8'.
        """
        self.encoding = encoding

    def read(self, file_path: str) -> Dict:
        data = []
        with open(file_path, 'r', encoding=self.encoding) as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return {"data": data}

    def write(self, file_path: str, data: Dict) -> bool:
        try:
            if "data" not in data:
                raise ValueError(
                    "Data dictionary must contain a 'data' key with a list of rows.")
            with open(file_path, 'w', encoding=self.encoding, newline='') as file:
                writer = csv.DictWriter(
                    file, fieldnames=data["data"][0].keys())
                writer.writeheader()
                writer.writerows(data["data"])
            return True
        except Exception:
            return False


class TxtReadWriteStrategy(IReadWriteStrategy):
    """Strategy for reading and writing plain text files."""

    def __init__(self, encoding: str = 'utf-8') -> None:
        """
        Initializes TxtReadWriteStrategy with an optional encoding.

        Args:
            encoding (str): The file encoding to use. Default is 'utf-8'.
        """
        self.encoding = encoding

    def read(self, file_path: str) -> Dict:
        with open(file_path, 'r', encoding=self.encoding) as file:
            text = file.read()
        return {"text": text}

    def write(self, file_path: str, data: Dict) -> bool:
        try:
            if "text" not in data:
                raise ValueError("Data dictionary must contain a 'text' key.")
            with open(file_path, 'w', encoding=self.encoding) as file:
                file.write(data["text"])
            return True
        except Exception:
            return False
