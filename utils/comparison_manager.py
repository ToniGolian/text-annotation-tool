import re
from typing import Dict, List, Tuple, Union
from controller.interfaces import IController
from model.interfaces import IDocumentModel
from utils.interfaces import ITagProcessor


class ComparisonManager:
    def __init__(self, controller: IController, tag_processor: ITagProcessor):
        self._controller = controller
        self._tag_processor = tag_processor
        self._similarity_threshold = 0.95
        self._max_lookahead = 10

    def extract_comparison_data(self, documents: IDocumentModel) -> Dict[str, Union[str, List[str]]]:
        texts = [document.get("text", "") for document in documents]
        texts = [self._prepare_text_for_comparison(
            text) for text in texts]
        clean_texts = [self._tag_processor.delete_all_tags_from_text(
            text) for text in texts]

        # compare if closely the same
        # merge due to mergeoptions
        # adjust indices in single documents
        # compare sentences

    def align_similar_texts(self, texts: List[List[str]], clean_texts: List[List[str]]) -> Tuple[List[List[str]], List[List[str]]]:
        aligned_texts = [[] for _ in texts]
        aligned_clean_texts = [[] for _ in clean_texts]

        # Convert clean_texts to sets for comparison
        clean_text_sets = [set(map(tuple, clean_text))
                           for clean_text in clean_texts]

        # Find the intersection across all clean_texts
        common_sentences = set.intersection(*clean_text_sets)

        # Check if all clean_texts are fully identical
        if all(clean_text_set == common_sentences for clean_text_set in clean_text_sets):
            return texts, clean_texts

        # Compute intersection ratios
        intersection_ratios = [
            len(common_sentences) / len(clean_text_set) for clean_text_set in clean_text_sets
        ]

        # Ensure all clean_texts meet the required similarity threshold
        if not all(ratio >= self._similarity_threshold for ratio in intersection_ratios):
            raise ValueError(
                "Clean texts do not meet the required similarity threshold.")

        # align_option=self._controller.get_align_option()
        #!DEBUG
        align_option = "union"
        #!END DEBUG

        # if align_option.lower() == "union":
        max_text_length = len(max(clean_texts, key=len))
        for text, clean_text in zip(texts, clean_texts):
            padding = [""]*(max_text_length-len(clean_text))
            text += padding
            clean_text += padding

        return aligned_texts, aligned_clean_texts

    def _prepare_text_for_comparison(self, text: str) -> List[str]:
        """
        Splits the given text into sentences and removes leading/trailing whitespace 
        as well as non-visible characters from each sentence.

        This method ensures that each sentence is cleaned by stripping whitespace 
        and removing any non-visible characters.

        Args:
            text (str): The input text to be prepared for comparison.

        Returns:
            List[str]: A list of cleaned sentences.
        """
        return [re.sub(r'\s+', ' ', sentence.strip()) for sentence in text.split("\n\n")]

    def _find_differing_sentences(self, texts: List[str]) -> List[int]:
        pass
