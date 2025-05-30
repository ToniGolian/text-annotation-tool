from dataclasses import dataclass


@dataclass
class SearchResult:
    """
    Represents a search term and its position in the text.

    Instances of this class store the matched term along with its
    start and end character indices in the original text, enabling
    functionalities such as highlighting and contextual lookup.

    Attributes:
        term (str): The matched search term.
        start (int): The start index of the term in the text.
        end (int): The end index of the term in the text.
    """
    term: str
    start: int
    end: int
