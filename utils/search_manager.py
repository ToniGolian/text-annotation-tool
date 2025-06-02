from enums.search_types import SearchType
from input_output.file_handler import FileHandler
from model.search_model import SearchModel


class SearchManager:
    def __init__(self, file_handler: FileHandler = None) -> None:
        """        Initializes the search manager with an optional file handler.
        Args:
            file_handler (FileHandler, optional): An instance of FileHandler for file operations.
        """
        self._file_handler = file_handler

    def calculate_model(self, tag_type: str, search_type) -> SearchModel:
        """
        Calculates a new SearchModel for the specified tag type and search type.

        Args:
            tag_type (str): The tag type for which the model should be calculated.
            search_type: The calculation mode (e.g., database, file system).

        Returns:
            SearchModel: A new instance of SearchModel with the calculated results.
        """
        if search_type not in [SearchType.DB, SearchType.MANUAL]:
            raise ValueError("Invalid search type specified.")
        search_model = SearchModel()
        if search_type == SearchType.DB:
            # Load the database dictionary
            db_dict = self._file_handler.read_db_dict(tag_type=tag_type)
            # perform the search based on the database dictionary
            # todo: Implement the actual database search logic
            search_results = []
            # store the results in the search_model
            raise NotImplementedError("Database search logic not implemented.")
        elif search_type == SearchType.MANUAL:
            # todo: Implement manual search logic
            search_results = []
            # Placeholder for manual search logic
            raise NotImplementedError("Manual search logic not implemented.")

        search_model.set_results(search_results)
        search_model.validate()

        return search_model
