import csv
import re


class CSVDBConverter:
    def __init__(self, file_handler=None) -> None:
        """Initialize the CSVConverter."""
        # create the file handler
        self._file_handler = file_handler

        self._key_column = None
        self._output_columns = None
        self._display_columns = None
        self._delimiter = None
        self._dict_delimiters = None

        self._prefixes = None
        self._postfixes = None
        self._infixes = None

    def create_dict(self, tag_type: str):
        """Creates a dictionary for the specified tag type using data from a CSV file.

        Args:
            tag_type (str): The type of tag for which the dictionary is created.

        Returns:
            dict: A dictionary containing the data for the specified tag type.
        """
        tag_type = tag_type.lower()
        # load columns and options
        self._load_options_and_columns(tag_type)
        # get the file path for the csv file
        file_path = self._file_handler.resolve_path(
            "project_db_csv_folder", f"{tag_type}_csv_db.csv")
        # build dict with the csv file
        dictionary = self._build_dict(file_path=file_path)

        return dictionary

    def _build_dict(self, file_path: str) -> dict:
        """Create the dictionary from the CSV file.
        This function reads the CSV file, processes each row, and builds a nested dictionary structure based on the specified key column, delimiters, and other specified information in the configuration file.

        The structure is built such that each key is a word from the key column, and its value is a dictionary containing three keys:
            - "display": A list of possible display strings for the word.
            - "output": A list of possible output strings for the word.
            - "children": A dictionary of sub-words, where each sub-word is a key with its own nested structure.

        Words are considered sub-words if they start with the current word followed by a delimiter specified in the configuration file.

        Args:
            file_path (str): The path to the CSV file to read.
        Returns:
            dict: The nested dictionary.
        """
        # init the dictionary
        our_dict = {}
        # get the column number
        current_word = ""
        # save the previous read row in case we need to reset the reader to it
        with open(file_path, "r", encoding="utf-8") as file:
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
                # if key already exists, we need to update the existing dict
                # if not, we create a new dict for the current word
                existing_dict = our_dict.get(current_word, {
                    "display": [],
                    "output": [],
                    "children": {}
                })
                # create the dict layer for the current word
                # this will create a new dict for the current word if it does not exist, or update the existing dict
                # with the current word and its children
                our_dict[current_word] = self._create_dict_layer(
                    existing_dict,
                    current_word,
                    row,
                    lookahead_row,
                    reader,
                )

        return our_dict

    def _initialize_config_fields(self, config: dict):
        """
        Initializes the internal fields of the CSVDBConverter based on the provided configuration dictionary.
        Args:
            config (dict): A dictionary containing the configuration for the CSVDBConverter.
        Raises:
            KeyError: If the configuration dictionary does not contain the expected keys.
        """
        self._key_column = config["columns"]["key_column"]
        self._output_columns = config["columns"]["output_columns"]
        self._display_columns = config["columns"]["display_columns"]
        self._delimiter = config["options"]["delimiter"]
        self._dict_delimiters = config["options"]["dict_delimiters"]
        self._prefixes = config["options"]["prefixes"]
        self._postfixes = config["options"]["postfixes"]
        self._infixes = config["options"]["infixes"]

    def _load_options_and_columns(self, tag_type: str) -> None:
        """
        Loads the dictionary configuration for a given tag type and initializes internal fields.

        Args:
            tag_type (str): The tag type whose config file should be loaded.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            ValueError: If the file content is malformed or unreadable.
        """
        try:
            config = self._file_handler.read_file(
                "project_db_config_folder", f"{tag_type}_config.json"
            )
            self._initialize_config_fields(config)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Configuration file not found. Please create a configuration file first."
            )
        except ValueError:
            raise ValueError(
                "Configuration file malformatted. Please check the file format."
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
            self._create_string(row, self._display_columns)]
        current_dict["output"] = [
            self._create_string(row, self._output_columns)]

        # get the next row and word if they exist
        next_row = lookahead_row
        if not next_row:
            return current_dict

        next_word = next_row[self._key_column]

        # check if a word starts with any combination of the current word + some delimiter
        starts_with_word = self._starts_with_current_word(
            next_word, current_word)

        while starts_with_word:
            # no subdict for identical words, but new display and output information
            if next_word == current_word:

                # append the display information of the following words, if they are exactly the same in the key column
                # their display and output information might be different, thus append them as well
                # this steps creates all entries for the drop down menu for display (and respective tagging information for output)
                current_dict["display"].append(
                    self._create_string(next_row, self._display_columns)
                )

                current_dict["output"].append(
                    self._create_string(next_row, self._output_columns)
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
            starts_with_word = self._starts_with_current_word(
                next_word, current_word)

        # now the next word is not starting with the current word anymore, thus do the next dict, then we need to reset the lookahead to the current row
        lookahead_row = next_row
        return current_dict

    def _strip_output_and_add_delimiter(self, col: int, entry: str) -> str:
        """
        Strip the postfix, prefix, and infix from the entry and add a delimiter.
        Args:
            col (int): The column number to check for prefixes, postfixes, and infixes.
            entry (str): The entry string from which to strip the postfix, prefix, and infix.
        Returns:
            str: The entry with the postfix, prefix, and infix stripped, followed by a delimiter.
        Raises:
            ValueError: If the entry is None or empty.
        """
        if not entry:
            return ""
        # Strip postfix, prefix, and infix in sequence
        stripped_entry = self._strip_prefix(col, entry)
        stripped_entry = self._strip_postfix(col, stripped_entry)
        stripped_entry = self._strip_infix(col, stripped_entry)

        # Add delimiter if the resulting string is not empty
        return f"{stripped_entry}{self._delimiter}" if stripped_entry else ""

    def _create_string(self, row: list[str], columns: list[int]) -> str:
        """
        Creates a concatenated string from the specified columns of a row.
        This method takes the values from the given columns, removes defined prefixes, postfixes, and infixes,
        adds a delimiter between the values, and returns the final processed string.

        Args:
            row (list[str]): The values of a row.
            columns (list[int]): The indices of the columns to use.

        Returns:
            str: The processed and concatenated string.
        """
        output = ""
        for col in columns:
            output_stripped_post_and_prefix = self._strip_output_and_add_delimiter(
                col, row[col]
            )
            output += output_stripped_post_and_prefix

        return output[: -len(self._delimiter)]

    def _strip_postfix(self, column_number: int, entry: str) -> str:
        """
        Removes a specified postfix from the given entry string based on the column number.

        Args:
            column_number (int): The index of the column whose postfixes should be considered.
            entry (str): The string entry from which to remove the postfix.

        Returns:
            str: The entry string with the postfix removed if a matching postfix is found; otherwise, returns the original entry.

        Notes:
            - The method checks if the specified column has any postfixes defined in `self._postfixes`.
            - If a matching postfix is found at the end of the entry, it is removed.
            - If no matching postfix is found, the original entry is returned unchanged.
        """
        postfixes = self._postfixes
        # check if the column has a postfix that should be removed
        if not (str(column_number) in postfixes):
            return entry

        postfixes = self._postfixes[str(column_number)]

        for postfix in postfixes:

            if postfix != "" and entry.endswith(postfix):
                return entry[: -len(postfix)]  # remove exact matched suffix

        return entry  # no postfix matched

    def _strip_infix(self, column_number: int, entry: str) -> str:
        """
        Removes specified infixes from a string entry based on the column number.

        Args:
            column_number (int): The column index to check for infixes.
            entry (str): The string from which infixes should be removed.

        Returns:
            str: The entry string with all matching infixes removed.

        Notes:
            - Infixes to be removed are defined in self._infixes, which should be a mapping from column numbers (as strings) to lists of infix strings.
            - If no infixes are specified for the given column, the entry is returned unchanged.
            - All occurrences of the infixes are removed, and removal is done in reverse order to avoid index shifting issues.
        """
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

    def _strip_prefix(self, column_number: int, entry: str) -> str:
        """Strip the prefix from the entry based on the column number.
        Args:
            column_number (int): The column number to check for prefixes.
            entry (str): The entry string from which to strip the prefix.
        Returns:
            str: The entry with the prefix stripped, or the original entry if no prefix matched.
        """
        # check if the column has a prefix that should be removed
        if not (str(column_number) in self._prefixes):
            return entry

        prefixes = self._prefixes[str(column_number)]

        for prefix in prefixes:
            if prefix != "" and entry.startswith(prefix):
                return entry[len(prefix):]  # remove matched prefix

        return entry  # no prefix matched

    def _starts_with_current_word(self, entry: str, starting_word: str) -> bool:
        """
        Check if the given entry starts with the specified starting word or with the starting word followed by any delimiter.

        Args:
            entry (str): The string to check.
            starting_word (str): The word to check for at the start of the entry.

        Returns:
            bool: True if the entry starts with the starting_word or with starting_word followed by any delimiter in self._dict_delimiters, False otherwise.
        """
        # check if the entry starts with a " "
        if entry == starting_word:
            return True
        for prefix in self._dict_delimiters:
            if entry.startswith(starting_word + prefix):
                return True
        return False
