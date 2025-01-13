import json
from input_output.interfaces import IFileHandler
from utils.interfaces import IListManager


class ListManager(IListManager):
    def __init__(self, file_handler: IFileHandler):
        self._file_handler = file_handler

    def get_abbreviations(self) -> set[str]:
        """
            Loads abbreviations from a JSON file and returns the list of German abbreviations.

            Arguments:
                file_path (str): The path to the JSON file containing abbreviations. 
                                Defaults to "app_data/abbreviations.json".

            Returns:
                List[str]: A list of German abbreviations as strings.

            Raises:
                FileNotFoundError: If the file does not exist.
                json.JSONDecodeError: If the file is not valid JSON.
                KeyError: If the "german" key is missing in the JSON file.
            """
        file_path = "app_data/abbreviations.json"
        try:
            # Load the JSON file
            with open(file_path, "r") as file:
                data = json.load(file)

            # Extract and return the list of German abbreviations
            return set(data["german"])
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in '{file_path}': {e.msg}", e.doc, e.pos)
        except KeyError:
            raise KeyError(
                f"The key 'german' is missing in the JSON file '{file_path}'.")
