from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class SearchResult:
    """
    Represents a search result with its position in the original text and associated annotation data.

    This class stores a matched expression from a dictionary-based database search. It includes both the
    textual span in the source document and structured metadata for UI display and downstream annotation.

    Attributes:
        term (str): The matched phrase as found in the original text.
        start (int): The character index where the match starts (inclusive).
        end (int): The character index where the match ends (exclusive).
        db_data (Optional[List[Tuple[str, str]]]): A list of (display, output) pairs for UI and annotation.
        tag_type (str): The category of annotation associated with this search result.
    """

    term: str
    start: int
    end: int
    db_data: Optional[List[Tuple[str, str]]] = field(default=None)
    tag_type: str = field(default="")

    def get_display_list(self) -> List[str]:
        """
        Returns the list of display strings extracted from the db_data pairs.

        Returns:
            List[str]: A list of display strings, or an empty list if db_data is None.
        """
        if self.db_data is None:
            return []
        return [display for display, _ in self.db_data]

    def get_output_for_display(self, display_value: str) -> Optional[str]:
        """
        Returns the corresponding output value for a given display string.

        Args:
            display_value (str): The selected display string.

        Returns:
            Optional[str]: The corresponding output value, or None if not found or db_data is None.
        """
        if self.db_data is None:
            return None
        for display, output in self.db_data:
            if display == display_value:
                return output
        return None
