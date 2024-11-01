from typing import Dict
from io.interfaces import IProcessorStrategy


class PdfProcessor(IProcessorStrategy):
    """Processes raw PDF data into document format."""

    def __init__(self, data: Dict) -> None:
        """
        Initializes PdfProcessor with raw PDF data.

        Args:
            data (Dict): Raw data extracted from a PDF file.
                Expected format:
                    {"pages": [str, str, ...]} - A list of strings, each representing the text of a PDF page.
        """
        super().__init__(data)

    def process(self) -> Dict:
        """
        Processes the raw PDF data into document format.

        Returns:
            Dict: A dictionary with structured, processed data.
                Format:
                    {"processed_text": str} - Concatenated text of all PDF pages.
        """
        structured_data = {"processed_text": ""}
        for page_text in self.data.get("pages", []):
            structured_data["processed_text"] += page_text + "\n"
        return structured_data


class TxtProcessor(IProcessorStrategy):
    """Processes raw TXT data into document format."""

    def __init__(self, data: Dict) -> None:
        """
        Initializes TxtProcessor with raw text data.

        Args:
            data (Dict): Raw data extracted from a text file.
                Expected format:
                    {"text": str} - A single string representing the entire content of the text file.
        """
        super().__init__(data)

    def process(self) -> Dict:
        """
        Processes the raw TXT data into document format.

        Returns:
            Dict: A dictionary with structured, processed data.
                Format:
                    {"processed_text": str} - Processed text from the raw TXT data.
        """
        structured_data = {"processed_text": self.data.get("text", "")}
        return structured_data


class CsvProcessor(IProcessorStrategy):
    """Processes raw CSV data into document format."""

    def __init__(self, data: Dict) -> None:
        """
        Initializes CsvProcessor with raw CSV data.

        Args:
            data (Dict): Raw data extracted from a CSV file.
                Expected format:
                    {"data": [Dict[str, str], ...]} - A list of dictionaries, each representing a row in the CSV file.
        """
        super().__init__(data)

    def process(self) -> Dict:
        """
        Processes the raw CSV data into document format.

        Returns:
            Dict: A dictionary with structured, processed data.
                Format:
                    {"processed_data": List[Dict[str, str]]} - A list of dictionaries representing processed CSV data.
        """
        structured_data = {"processed_data": self.data.get("data", [])}
        # Additional processing of CSV data could be added here if needed
        return structured_data
