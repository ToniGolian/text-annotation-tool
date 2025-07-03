import hashlib
import os
from pathlib import Path
from typing import List
import re
from typing import Dict, List, Tuple, Union
from controller.interfaces import IController
from model.annotation_document_model import AnnotationDocumentModel
from model.interfaces import IDocumentModel
from model.tag_model import TagModel
from utils.interfaces import ITagProcessor


class ComparisonManager:
    def __init__(self, controller: IController, tag_processor: ITagProcessor):
        self._controller = controller
        self._tag_processor = tag_processor
        self._similarity_threshold = 0.90
        self._max_lookahead = 10
        self._common_text: List[str] = []
        self._differing_to_global: List[int] = []

    def extract_comparison_data(self, documents: List[IDocumentModel]) -> Dict[str, Union[List[str], List[List[str]], List[int]]]:
        """
        Extracts comparison-relevant data from a list of annotated documents.

        This method prepares tagged and clean text versions from each document, aligns the sentences
        across annotators using the configured alignment strategy (union or intersection), and
        identifies sentence-level differences by removing ID-related attributes. The results are
        stored internally and returned as structured data.

        Args:
            documents (List[IDocumentModel]): A list of annotated documents to compare.

        Returns:
            Dict[str, Union[List[str], List[List[str]], List[int]]]: A dictionary containing:
                - "comparison_sentences" (List[List[str]]): A list of lists where the first element contains
                raw sentences and each subsequent list contains differing tagged sentences per annotator.
                - "differing_to_global" (List[int]): A list of indices. For each differing sentence (by index in
                `comparison_sentences`), this list contains the corresponding sentence index in the full
                merged text.
                - "merged_document" (IDocumentModel): The document model representing the merged output text.
        """

        tagged_texts = self._prepare_tagged_texts(documents)
        raw_texts = self._extract_clean_texts(tagged_texts)
        aligned_tagged, aligned_clean = self._align_similar_texts(
            tagged_texts, raw_texts)

        self._common_text = aligned_tagged[0]
        raw_text = aligned_clean[0]

        self._extract_differing_tagged_sentences(
            raw_text, aligned_tagged)

        start_sentences, start_tags = self.get_start_data(0)

        merged_document = self._create_merge_document()

        #! remove
        self._controller.find_equivalent_tags(
            documents, merged_document)
        #! end remove

        return {
            "comparison_sentences": self._comparison_sentences,
            "differing_to_global": self._differing_to_global,
            "merged_document": merged_document,
            "start_data": (start_sentences, start_tags)
        }

    def get_start_data(self, sentence_index: int = 0, comparison_sentences=None) -> Tuple[List[str], List[List[TagModel]]]:
        """
        Retrieves the initial sentences and their associated tags for comparison.

        This method returns the first sentence and its tags from the comparison data,
        which can be used to initialize a comparison view or display.

        Args:
            sentence_index (int): The index of the sentence to retrieve. Defaults to 0.

        Returns:
            Tuple[List[str], List[List[TagModel]]]: A tuple containing:
                - A list with the first sentence.
                - A list of lists, where each inner list contains TagModel objects for that sentence.
        """
        if not comparison_sentences:
            comparison_sentences = self._comparison_sentences
        start_sentences = [
            sentences[sentence_index] for sentences in comparison_sentences]
        start_tags = [[TagModel(tag_data) for tag_data in self._tag_processor.extract_tags_from_text(
            sentence)] for sentence in start_sentences]
        return start_sentences, start_tags

    def _align_similar_texts(self, texts: List[List[str]], clean_texts: List[List[str]]) -> Tuple[List[List[str]], List[List[str]]]:
        """
        Aligns multiple similar texts by merging them using either union or intersection.

        This method aligns the input texts while maintaining sentence order, handling missing
        sentences, and ensuring structural consistency between all input lists. The alignment
        can be performed using one of two strategies:

        - "union": Includes all sentences from all texts, preserving their relative order.
        - "intersection": Retains only sentences that appear in all texts.

        The function first checks if the texts are fully identical. If they are not, it
        computes an intersection ratio and ensures that all texts meet a predefined similarity
        threshold before proceeding with the chosen alignment strategy.

        Args:
            texts (List[List[str]]): A list of texts, where each text is represented as a list of sentences.
            clean_texts (List[List[str]]): The same texts as in `texts`, but with tags removed.

        Returns:
            Tuple[List[List[str]], List[List[str]]]: A tuple containing two lists:
                - The aligned texts with original content.
                - The aligned clean texts with tags removed.

        Raises:
            ValueError: If the similarity threshold is not met, meaning the texts are not similar enough.
            ValueError: If ambiguous sentence alignment is detected (e.g., reordering or duplicate mismatched references).
            ValueError: If no valid alignment option ("union" or "intersection") is selected.

        """
        # Define helpers

        def get_current_elements():
            """Retrieves a list of clean sentences corresponding to the current indices"""
            return [clean_text[index] if index < len(clean_text) else "" for clean_text, index in zip(clean_texts, sentence_indices)]

        def are_clean_sentences_similar(sentences: List[str]) -> bool:
            """Checks if all sentences in a list are similar"""
            return all(sentence == sentences[0] for sentence in sentences[1:])

        def append_elements(indices_to_append) -> None:
            """Appends the elements corresponding to the indices to texts and clean texts"""
            for aligned_text, aligned_clean_text, (text_index, sentence_index) in zip(aligned_texts, aligned_clean_texts, indices_to_append):
                aligned_text.append(texts[text_index][sentence_index])
                aligned_clean_text.append(
                    clean_texts[text_index][sentence_index])

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
            # Find the lowest similarity ratio
            min_ratio = min(intersection_ratios)
            raise ValueError(
                f"Similarity threshold not met. A text has only {min_ratio:.2%} overlap with the others, but at least {self._similarity_threshold:.2%} is required. The texts are likely not the same."
            )

        aligned_texts = [[] for _ in texts]
        aligned_clean_texts = [[] for _ in clean_texts]
        align_option = self._controller.get_align_option()

        sentence_indices = [0]*len(clean_texts)
        while any(index < len(clean_text) for clean_text, index in zip(clean_texts, sentence_indices)):
            current_elements = get_current_elements()
            if are_clean_sentences_similar(current_elements):
                indices_to_append = [(text_index, sentence_index)
                                     for text_index, sentence_index in enumerate(sentence_indices)]
                append_elements(indices_to_append)
                for i in range(len(sentence_indices)):
                    sentence_indices[i] += 1
                continue

            # Handle non aligning sentences
            next_candidates = []  # List of tuples (sentence, text_index)

            # Check if sentence appears later in other texts
            buffers = [clean_text[index+1:index+self._max_lookahead]
                       for clean_text, index in zip(clean_texts, sentence_indices)]

            for text_index, sentence in enumerate(current_elements):
                if all(sentence not in buffer for buffer in buffers):
                    next_candidates.append((sentence, text_index))

            # If intersection mode is active and next_candidates is empty, this means that
            # all current sentences exist somewhere in the upcoming buffers, which likely
            # indicates a reordering or duplicate sentences with mismatched references.
            if not next_candidates:
                if align_option == "intersection":
                    raise ValueError(
                        "Ambiguous sentence alignment detected: Possible reordering or duplicate sentences with mismatched references."
                    )
                if align_option == "union":
                    # just pick the sentence from the first text
                    next_candidates = [current_elements[0]]
                raise ValueError("No align option selected")

            # drop the sentences, which are not in all texts, if alignoption is intersection
            if align_option.lower() == "intersection":
                for _, text_index in next_candidates:
                    sentence_indices[text_index] += 1
                continue

                # Check if potential next sentence is unique
            if not are_clean_sentences_similar([sentence for sentence, _ in next_candidates]):
                # Count occurrences of sentences
                count = {}
                for sentence, _ in next_candidates:
                    count[sentence] = count.get(sentence, 0) + 1

                # Find the most frequent sentence
                most_frequent_sentence = max(count, key=count.get)

                # Keep only the most frequent sentence with corresponding indices
                next_candidates = [
                    item for item in next_candidates if item[0] == most_frequent_sentence]

            # Extract first selected index and apply to all texts
            _, text_index = next_candidates[0]
            indices_to_append = [
                (text_index, sentence_indices[text_index])]*len(clean_texts)

            append_elements(indices_to_append)

            # Increment indices for the selected sentences
            for _, text_index in next_candidates:
                sentence_indices[text_index] += 1

        return aligned_texts, aligned_clean_texts

    def _create_merge_document(self) -> AnnotationDocumentModel:
        """
        Creates a merged annotation document from the current comparison data.
        This method constructs a new `AnnotationDocumentModel` instance that contains
        the merged text from all compared documents, along with metadata tags.
        """
        text = "\n\n".join(self._common_text)
        merge_document_data = {
            "document_type": "comparison",
            "file_path": "",
            "file_name": "",
            "meta_tags": {},
            "text": text,
        }
        return AnnotationDocumentModel(merge_document_data)

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

    def _prepare_tagged_texts(self, documents: List[IDocumentModel]) -> List[List[str]]:
        """
        Extracts and splits the raw tagged text from each document into cleaned sentence lists.

        This method accesses the 'text' field from each document, splits it into sentences,
        and normalizes whitespace and invisible characters for consistent comparison.

        Args:
            documents (List[IDocumentModel]): The documents to be processed.

        Returns:
            List[List[str]]: A list of sentence lists, one per document.
        """
        tagged_texts = [self._prepare_text_for_comparison(
            document.get_text()) for document in documents]
        return tagged_texts

    def _extract_clean_texts(self, tagged_texts: List[List[str]]) -> List[List[str]]:
        """
        Removes all tags from the tagged sentence lists to produce raw textual content.

        This method converts each tagged sentence into plain text by stripping all markup,
        which is used for alignment and comparison purposes.

        Args:
            tagged_texts (List[List[str]]): A list of sentence lists containing tagged content.

        Returns:
            List[List[str]]: A list of sentence lists with all tags removed.
        """
        return [[self._tag_processor.delete_all_tags_from_text(sentence) for sentence in text]
                for text in tagged_texts]

    def _extract_differing_tagged_sentences(self, raw_text: List[str], tagged_texts: List[List[str]]) -> None:
        """
        Extracts differing sentences across multiple tagged versions of a text
        and stores them in internal instance variables.

        This method compares aligned sentences from multiple tagged texts
        after removing ID and IDREF attributes. If differences are found,
        the corresponding raw sentence is added to the common text, and the
        differing tagged versions are stored for later use.

        Side effects:
            - Updates `self._comparison_sentences`: A list of lists where the first
            list contains the untagged raw sentences and the remaining lists contain
            differing tagged sentences per annotator.
            - Updates `self._common_text`: A dictionary mapping sentence indices to
            the corresponding raw sentence, used as shared reference text.
            - Updates `self._differing_to_global`: A list mapping local differing sentence index
            to global sentence index in the merged document.
        """
        self._comparison_sentences = [[] for _ in range(len(tagged_texts) + 1)]
        self._differing_to_global = []

        # Iterate over the sentences from all tagged texts simultaneously
        for global_index, sentences in enumerate(zip(*tagged_texts)):
            # Remove ID and IDREF attributes from all sentences
            cleaned_sentences = [
                self._tag_processor.remove_ids_from_tags(sentence)
                for sentence in sentences
            ]

            # Check if all cleaned sentences are identical
            if any(sentence != cleaned_sentences[0] for sentence in cleaned_sentences[1:]):
                raw_sentence = raw_text[global_index]

                # Add the differing sentence and its variants
                self._comparison_sentences[0].append(raw_sentence)
                for sentence_list, sentence in zip(self._comparison_sentences[1:], sentences):
                    sentence_list.append(sentence)

                self._common_text[global_index] = raw_sentence
                self._differing_to_global.append(global_index)
