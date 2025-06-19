from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchResult:
    """
    Represents a search result and its character-level position in the original text.

    This class is used to store information about a successfully matched expression from a database
    dictionary search. In addition to the matched string itself, it tracks the exact character offsets 
    within the full document text, as well as any metadata relevant for display or annotation.

    Attributes:
        term (str): The matched phrase as found in the text.
        start (int): Start character index of the match in the text.
        end (int): End character index (exclusive) of the match in the text.
        display (Optional[List[str]]): Display alternatives for UI purposes.
        output (Optional[List[str]]): Output alternatives for annotation tagging.
        tag_type (str): The type of tag associated with this search result.
    """
    term: str
    start: int
    end: int
    display: Optional[List[str]] = field(default=None)
    output: Optional[List[str]] = field(default=None)
    tag_type: str = field(default="")
