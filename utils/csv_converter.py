import csv
from input_output.file_handler import FileHandler
import re


class CSVConverter:
    def __init__(self):
        """Initialize the CSVConverter."""
        # create the file handler
        self._file_handler = FileHandler()

        self._file_path = ""
        self._dict_path = ""
        self._dict_config_path = ""

        self._key_column = None
        self._output_columns = None
        self._display_columns = None
        self._delimiter = None
        self._dict_delimiters = None

        self._prefixes = None
        self._postfixes = None
        self._infixes = None

    def create_dict(self, file_name: str):
        """Create the dictionary from the CSV file and the belonging configuration file and save the dictionary to a JSON file."""
        # init paths
        self._update_paths(file_name)
        # load columns and options
        self._load_options_and_columns()
        # build dict with the csv file
        dictionary = self._build_dict()
        # save the dict to a file
        self._file_handler.write_file(self._dict_path, dictionary)

        return dictionary

    def _build_dict(self) -> dict:
        """Create the dictionary from the CSV file.
        This function reads the CSV file, processes each row, and builds a nested dictionary structure based on the specified key column, delimiters, and other specified information in the configuration file.

        The structure is built such that each key is a word from the key column, and its value is a dictionary containing three keys:
            - "display": A list of possible display strings for the word.
            - "output": A list of possible output strings for the word.
            - "children": A dictionary of sub-words, where each sub-word is a key with its own nested structure.

        Words are considered sub-words if they start with the current word followed by a delimiter specified in the configuration file.

        Returns:
            dict: The nested dictionary.
        """
        # init the dictionary
        our_dict = {}
        # get the column number
        current_word = ""
        # save the previous read row in case we need to reset the reader to it
        with open(self._file_path, "r") as file:
            reader = csv.reader(file)
            lookahead_row = next(reader, None)

            # skip the header
            next(reader)
            # continue to advance the reader until the end is reached
            while lookahead_row is not None:
                row = lookahead_row  # advances reader
                lookahead_row = next(reader, None)  # get the next row
                # gets the first word
                current_word = row[self._key_column]
                # creates dict with key as the first word + recursive call for the sub-dictionaries
                our_dict[current_word] = self._create_dict_layer(
                    {},
                    current_word,
                    row,
                    lookahead_row,
                    reader,
                )

        return our_dict

    def _initialize_config_fields(self, config: dict):
        """Initialize the configuration fields from the config dictionary."""
        self._key_column = config["columns"]["key_column"]
        self._output_columns = config["columns"]["output_columns"]
        self._display_columns = config["columns"]["display_columns"]
        self._delimiter = config["options"]["delimiter"]
        self._dict_delimiters = config["options"]["dict_delimiters"]
        self._prefixes = config["options"]["prefixes"]
        self._postfixes = config["options"]["postfixes"]
        self._infixes = config["options"]["infixes"]

    def _load_options_and_columns(self):
        """Update the options and columns from file."""
        try:
            self._file_handler.read_file(self._dict_config_path)
            # Check if the options and columns from file
            config = self._file_handler.read_file(self._dict_config_path)
            # init all config fields
            self._initialize_config_fields(config)
            return True
        except FileNotFoundError:
            raise (
                "Configuration file not found. Please create a configuration file first.")
        except ValueError:
            raise ValueError(
                "Configuration file malformatted. Please check the file format.")

    def _update_paths(self, file_name: str):
        # set original path for the csv basis file
        self._file_path = self._file_handler._convert_path_to_os_specific(
            f"./app_data/project_data/{file_name}.csv"
        )

        # set the dict saving/loading path
        self._dict_path = self._file_handler._convert_path_to_os_specific(
            f"./app_data/project_data/{file_name}.json"
        )

        # set the saving/loading configuration path
        self._dict_config_path = self._file_handler._convert_path_to_os_specific(
            f"./app_data/project_config/db_config/{file_name}_config.json"
        )

    def _create_dict_layer(
        self,
        current_dict: dict,
        current_word: str,
        row: list[str],
        lookahead_row: list[str] | None,
        reader: csv.reader,
    ) -> dict:
        """
        Create a new layer in the dictionary based on the current word and row.
        This function recursively creates a nested dictionary structure based on the current word and the next words in the CSV file.
        Args:
            current_dict (dict): The current dictionary to update.
            current_word (str): The current word to use as a key.
            row (list[str]): The current row from the CSV file.
            lookahead_row (list[str] | None): The next row in the CSV file, or None if there are no more rows.
            reader (csv.reader): The CSV reader object to read the next rows.
        Returns:
            dict: The updated dictionary with the current word and its children.
        """

        # this is the dict for the next layer
        current_dict["children"] = {}
        # create the display and output information for the current word: output information will be used for the tagging and display information for the full description for menu
        current_dict["display"] = [
            self.create_string(row, self._display_columns)]
        current_dict["output"] = [
            self.create_string(row, self._output_columns)]

        # get the next row and word if they exist
        next_row = lookahead_row
        if not next_row:
            return current_dict

        next_word = next_row[self._key_column]

        # check if a word starts with any combination of the current word + some delimiter
        starts_with_word = self.starts_with_current_word(
            next_word, current_word)

        while starts_with_word:
            # no subdict for identical words, but new display and output information
            if next_word == current_word:

                # append the display information of the following words, if they are exactly the same in the key column
                # their display and output information might be different, thus append them as well
                # this steps creates all entries for the drop down menu for display (and respective tagging information for output)
                current_dict["display"].append(
                    self.create_string(next_row, self._display_columns)
                )

                current_dict["output"].append(
                    self.create_string(next_row, self._output_columns)
                )

            else:
                # if the word is not identical, we need to create a new subdict because the next word starts with the current word but is not exactly the same

                # use the children dict for the current word and append as a key the word
                sub_dict = current_dict["children"][next_word] = {}
                # for the next word: create a subdict recursively
                lookahead_row = next(reader, None)

                sub_dict = self._create_dict_layer(
                    sub_dict,
                    next_word,
                    next_row,
                    lookahead_row,
                    reader,
                )

            # check if we can proceed further and update the parameters
            next_row = next(reader, None)
            if not next_row:
                # If no more rows, return the current dictionary
                return current_dict

            # if we can proceed: update the parameters
            next_word = next_row[self._key_column]
            starts_with_word = self.starts_with_current_word(
                next_word, current_word)

        # now the next word is not starting with the current word anymore, thus do the next dict, then we need to reset the lookahead to the current row
        lookahead_row = next_row
        return current_dict

    def strip_output_and_add_delimiter(self, col: int, entry: str) -> str:
        """Strip the postfix, prefix, and infix from the entry and add a delimiter."""
        if not entry:
            return ""
        # Strip postfix, prefix, and infix in sequence
        stripped_entry = self.strip_prefix(col, entry)
        stripped_entry = self.strip_postfix(col, stripped_entry)
        stripped_entry = self.strip_infix(col, stripped_entry)

        # Add delimiter if the resulting string is not empty
        return f"{stripped_entry}{self._delimiter}" if stripped_entry else ""

    def create_string(self, row: list[str], columns: list[int]) -> str:
        """Create a string from the row based on the specified columns."""
        output = ""
        for col in columns:
            # stripping the postfix and prefix
            output_stripped_post_and_prefix = self.strip_output_and_add_delimiter(
                col, row[col]
            )
            # add the output
            output += output_stripped_post_and_prefix

        return output[: -len(self._delimiter)]

    def strip_postfix(self, column_number: int, entry: str) -> str:
        """Strip the postfix from the entry based on the column number."""
        postfixes = self._postfixes
        # check if the column has a postfix that should be removed
        if not (str(column_number) in postfixes):
            return entry

        postfixes = self._postfixes[str(column_number)]

        for postfix in postfixes:

            if postfix != "" and entry.endswith(postfix):
                return entry[: -len(postfix)]  # remove exact matched suffix

        return entry  # no postfix matched

    def strip_infix(self, column_number: int, entry: str) -> str:
        """Strip the infix from the entry based on the column number."""
        infixes = self._infixes
        # check if the column has a infix that should be removed
        if not (str(column_number) in infixes):
            return entry
        # Build a regex pattern that matches any infix literally
        pattern = "|".join(
            re.escape(infix) for infix in infixes[str(column_number)] if infix != ""
        )
        # Find all non-overlapping matches with start/end positions
        matches = list(re.finditer(pattern, entry))
        # Remove them in reverse order (so earlier indices aren't shifted)
        for match in reversed(matches):
            start, end = match.start(), match.end()
            entry = entry[:start] + entry[end:]

        return entry

    def strip_prefix(self, column_number: int, entry: str) -> str:
        """Strip the prefix from the entry based on the column number."""
        # check if the column has a prefix that should be removed
        if not (str(column_number) in self._prefixes):
            return entry

        prefixes = self._prefixes[str(column_number)]

        for prefix in prefixes:
            if prefix != "" and entry.startswith(prefix):
                return entry[len(prefix):]  # remove matched prefix

        return entry  # no prefix matched

    def starts_with_current_word(self, entry: str, starting_word: str) -> bool:
        """Check if the entry starts with the current word or a delimiter."""
        # check if the entry starts with a " "
        if entry == starting_word:
            return True
        for prefix in self._dict_delimiters:
            if entry.startswith(starting_word + prefix):
                return True
        return False


# columns = {"key_column": 4, "output_columns": [0], "display_columns": [2, 0]}

# options = {
#     # how to separate columns for the display string and output string
#     "delimiter": " | ",
#     # how to separate the dictionary keys, create a subdict if keys are separated by any of these delimiters e.g. "Berlin Bahnhof" would then be "Berlin" with subdict "Berlin Bahnhof"
#     "dict_delimiters": ["|", "-", "/", ",", ";", ":", "_", " "],
#     # which prefixes to remove per column: applied to both display and output columns
#     "prefixes": {2: ["AX_"]},
#     # which postfixes to remove per column: applied to both display and output columns
#     "postfixes": {2: [""]},
#     # which infixes to remove per column: applied to both display and output columns
#     "infixes": {2: [""]},
# }

file_name = "locationdata"
conv = CSVConverter()
dicti = conv.create_dict(file_name)
ic(dicti)
# ic(conv._options)
# ic(conv.dict["Aachen"])
