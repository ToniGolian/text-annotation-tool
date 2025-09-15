import re
from typing import Dict, List
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
        self._common_suffixes: List[str] = []
        # Characters to strip from words during search
        self._chars_to_strip: str = ""

    def calculate_db_search_model(self, tag_type: str, document_model: IDocumentModel, caller_id: str) -> SearchModel:
        """
        Calculates a new SearchModel for the specified tag type.

        Args:
            tag_type (str): The tag type for which the model should be calculated.
            document_model (IDocumentModel): The source document model.

        Returns:
            SearchModel: A new instance of SearchModel with the calculated results.
        """
        search_model = SearchModel(caller_id=caller_id)
        db_dict = self._file_handler.read_database_dict(tag_type=tag_type)
        text = document_model.get_text()

        # Improved tokenization: keeps XML elements together
        tokens = re.findall(r'<[^>]+>.*?</[^>]+>|[^\s]+', text)

        index = 0
        char_pos = 0

        while index < len(tokens):
            raw_token = tokens[index]

            # Remove XML tags if present and split into individual words
            if re.match(r'^<[^>]+>.*</[^>]+>$', raw_token):
                stripped_content = re.sub(r'^<[^>]+>', '', raw_token)
                stripped_content = re.sub(r'</[^>]+>$', '', stripped_content)
                # Insert the stripped words back into tokens, replacing the original
                stripped_words = stripped_content.split()
                tokens[index:index+1] = stripped_words
                continue  # Restart loop with new tokens
            else:
                stripped_token = raw_token

            match_token = stripped_token.rstrip(self._chars_to_strip)
            current_dict = None
            base_word = match_token

            if match_token in db_dict:
                current_dict = db_dict[match_token]
            else:
                for suffix in self._common_suffixes:
                    if match_token.endswith(suffix):
                        stripped = match_token[:-len(suffix)]
                        if stripped in db_dict:
                            current_dict = db_dict[stripped]
                            base_word = match_token
                            break
            if not current_dict:
                next_token_pos = text.find(raw_token, char_pos)
                char_pos = next_token_pos + len(raw_token)
                while char_pos < len(text) and text[char_pos].isspace():
                    char_pos += 1
                index += 1
                continue

            match_tokens = [stripped_token]
            last_valid_tokens = [stripped_token]
            match_data = current_dict
            last_valid_data = match_data
            end_index = index + 1

            # Check if the stripped token matches the expected length
            if len(match_token) == len(stripped_token):

                for j in range(index + 1, len(tokens)):
                    end_traversal = False
                    next_raw = tokens[j]
                    next_clean = next_raw.rstrip(self._chars_to_strip)
                    candidate_tokens = [token for token in tokens[index:j+1]]
                    candidate = " ".join(candidate_tokens)
                    stripped_candidate = candidate.rstrip(self._chars_to_strip)
                    if len(candidate) != len(stripped_candidate):
                        # If there was stripping the traversal ends
                        end_traversal = True
                    candidate = stripped_candidate

                    # candidate stripped of trailing special characters
                    # is a direct match in children
                    if candidate in match_data.get(
                            "children", {}):
                        match_tokens.append(next_clean)
                        last_valid_tokens = match_tokens.copy()
                        match_data = match_data["children"][candidate]
                        last_valid_data = match_data
                        end_index = j + 1
                        continue

                    suffix_free_candidate = candidate
                    for suffix in self._common_suffixes:
                        if candidate.endswith(suffix):
                            suffix_free_candidate = candidate[:-len(suffix)]

                    # If the candidate stripped of common suffixes is a direct match in children
                    # we can continue traversing
                    if suffix_free_candidate in match_data.get("children", {}):
                        match_tokens.append(next_clean)
                        last_valid_tokens = match_tokens.copy()
                        match_data = match_data["children"][suffix_free_candidate]
                        last_valid_data = match_data
                        end_index = j + 1
                        continue

                    tmp_lookahead = " ".join(
                        match_tokens + [next_clean])
                    if any(key.startswith(tmp_lookahead) for key in match_data.get("children", {}).keys()):
                        # If the next token is a valid continuation
                        match_tokens.append(next_clean)
                        end_index = j + 1
                    else:
                        # If the next token does not match, we stop traversing
                        end_traversal = True

                    if end_traversal:
                        # If we hit a token that does not match, we stop traversing
                        break

            matched_str_raw = " ".join(last_valid_tokens)
            matched_str_clean = matched_str_raw.rstrip(self._chars_to_strip)

            start_char = text.find(matched_str_clean, char_pos)

            end_char = start_char + len(matched_str_clean)

            result = SearchResult(
                term=matched_str_clean,
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

    def calculate_manual_search_model(self, options: Dict, document_model: IDocumentModel, caller_id: str) -> SearchModel:
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
            caller_id (str): The ID of the caller requesting the search.

        Returns:
            SearchModel: A populated SearchModel containing all matches.
        """
        search_model = SearchModel(caller_id=caller_id)
        search_model.set_search_options(options)

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

    def set_search_normalization(self, search_normalization: Dict) -> None:
        """
        Sets the search normalization parameters.

        Args:
            search_normalization (Dict): Dictionary containing normalization settings.
        """
        self._common_suffixes = search_normalization.get("common_suffixes", [])
        self._chars_to_strip = search_normalization.get("chars_to_strip", "")
