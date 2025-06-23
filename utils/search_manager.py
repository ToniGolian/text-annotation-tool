import re
from typing import Dict
from data_classes.search_result import SearchResult
from enums.search_types import SearchType
from input_output.file_handler import FileHandler
from model.interfaces import IDocumentModel
from model.search_model import SearchModel


class SearchManager:
    def __init__(self, file_handler: FileHandler = None) -> None:
        """        Initializes the search manager with an optional file handler.
        Args:
            file_handler (FileHandler, optional): An instance of FileHandler for file operations.
        """
        self._file_handler = file_handler
        self._common_suffixes = ["s"]  # todo load language dependet suffixes
        # Characters to strip from words during search
        self._chars_to_strip = ".,;:!?()[]{}\"'`~@#$%^&*_-+=|\\/<>"  # todo load from settings

    def calculate_db_search_model(self, tag_type: str, document_model: IDocumentModel) -> SearchModel:
        """
        Calculates a new SearchModel for the specified tag type and search type.

        Args:
            tag_type (str): The tag type for which the model should be calculated.
            search_type: The calculation mode (e.g., database, file system).

        Returns:
            SearchModel: A new instance of SearchModel with the calculated results.
        """

        search_model = SearchModel()
        db_dict = self._file_handler.read_db_dict(tag_type=tag_type)
        text = document_model.get_text()
        tokens = text.split()
        index = 0
        char_pos = 0  # current character position in the text

        while index < len(tokens):
            raw_token = tokens[index]

            # Strip tag-wrapped tokens only if they end with a closing tag
            stripped_token = raw_token
            if re.search(r"</[^>]+>$", raw_token):
                stripped_token = re.sub(r'^.*?>\s*|</[^>]+>$', '', raw_token)

            # Remove trailing punctuation characters
            word = stripped_token.rstrip(self._chars_to_strip)

            current_dict = None

            # Try exact match or suffix-stripped variant
            if word in db_dict:
                current_dict = db_dict[word]
            else:
                for suffix in self._common_suffixes:
                    if word.endswith(suffix):
                        stripped = word[:-len(suffix)]
                        if stripped in db_dict:
                            word = stripped
                            current_dict = db_dict[stripped]
                            break

            if not current_dict:
                # advance char_pos to the next token including spacing
                next_token_pos = text.find(raw_token, char_pos)
                char_pos = next_token_pos + len(raw_token)
                while char_pos < len(text) and text[char_pos].isspace():
                    char_pos += 1
                index += 1
                continue

            match_tokens = [stripped_token]
            match_data = current_dict
            last_valid_data = match_data
            end_index = index + 1

            for j in range(index + 1, len(tokens)):
                next_raw = tokens[j]
                next_clean = next_raw.rstrip(self._chars_to_strip)
                candidate_tokens = [
                    t.rstrip(self._chars_to_strip) for t in tokens[index:j+1]]
                candidate = " ".join(candidate_tokens)

                if candidate in match_data.get("children", {}):
                    match_tokens.append(next_clean)
                    match_data = match_data["children"][candidate]
                    last_valid_data = match_data
                    end_index = j + 1
                else:
                    for suffix in self._common_suffixes:
                        if candidate.endswith(suffix):
                            stripped_candidate = candidate[:-len(suffix)]
                            if stripped_candidate in match_data.get("children", {}):
                                match_tokens.append(next_clean)
                                match_data = match_data["children"][stripped_candidate]
                                last_valid_data = match_data
                                end_index = j + 1
                                break
                    else:
                        break

            matched_str = " ".join(match_tokens)
            start_char = text.find(matched_str, char_pos)
            end_char = start_char + len(matched_str)

            result = SearchResult(
                term=matched_str,
                start=start_char,
                end=end_char,
                db_data=list(zip(
                    last_valid_data.get("display", []),
                    last_valid_data.get("output", [])
                )),
                tag_type=tag_type,
                search_type=SearchType.DB,
            )

            search_model.add_result(result)

            index = end_index
            char_pos = end_char
            while char_pos < len(text) and text[char_pos].isspace():
                char_pos += 1

        return search_model

    def calculate_manual_search_model(self, options: Dict, document_model: IDocumentModel) -> SearchModel:
        """
        Calculates a SearchModel based on manual search parameters.

        This method scans the document text using the provided search term and options
        for case sensitivity, whole-word matching, and regex interpretation.

        Args:
            options (Dict): Dictionary containing search options:
                - "search_term" (str): The term to search for.
                - "case_sensitive" (bool): Whether the search should be case-sensitive.
                - "whole_word" (bool): Whether to match only whole words.
                - "regex" (bool): Whether to interpret the search term as a regular expression.
            document_model (IDocumentModel): The model containing the text to search.

        Returns:
            SearchModel: A populated SearchModel containing all matches.
        """
        import re

        search_model = SearchModel()
        text = document_model.get_text()
        term = options.get("search_term", "")
        if not term:
            return search_model

        flags = 0 if options.get("case_sensitive") else re.IGNORECASE
        if options.get("regex"):
            pattern = term
        else:
            pattern = re.escape(term)

        if options.get("whole_word"):
            pattern = r'\b' + pattern + r'\b'

        for match in re.finditer(pattern, text, flags):
            result = SearchResult(
                term=match.group(),
                start=match.start(),
                end=match.end(),
                search_type=SearchType.MANUAL,
            )
            search_model.add_result(result)
        search_model.validate()
        return search_model
