import re
from typing import Dict, List, Tuple, Union
from controller.interfaces import IController
from model.interfaces import IDocumentModel
from utils.interfaces import ITagProcessor


class ComparisonManager:
    def __init__(self, controller: IController, tag_processor: ITagProcessor):
        self._controller = controller
        self._tag_processor = tag_processor
        self._similarity_threshold = 0.90
        self._max_lookahead = 10

    def extract_comparison_data(self, documents: List[IDocumentModel]) -> Dict[str, Union[str, List[str]]]:
        texts = [document.get("text", "") for document in documents]
        texts = [self._prepare_text_for_comparison(
            text) for text in texts]
        clean_texts = [[self._tag_processor.delete_all_tags_from_text(
            sentence) for sentence in text] for text in texts]
        texts, clean_texts = self.align_similar_texts(texts, clean_texts)
        return texts, clean_texts

        # compare if closely the same
        # merge due to mergeoptions
        # adjust indices in single documents
        # compare sentences

    def align_similar_texts(self, texts: List[List[str]], clean_texts: List[List[str]]) -> Tuple[List[List[str]], List[List[str]]]:
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
        for clean_text in clean_texts:
            print(f"DEBUG {clean_text[:6]=}")

        # Find the intersection across all clean_texts
        common_sentences = set.intersection(*clean_text_sets)

        # Check if all clean_texts are fully identical
        if all(clean_text_set == common_sentences for clean_text_set in clean_text_sets):
            return texts, clean_texts

        # Compute intersection ratios
        intersection_ratios = [
            len(common_sentences) / len(clean_text_set) for clean_text_set in clean_text_sets
        ]

        print(f"DEBUG {intersection_ratios=}")
        # Ensure all clean_texts meet the required similarity threshold
        if not all(ratio >= self._similarity_threshold for ratio in intersection_ratios):
            # Find the lowest similarity ratio
            min_ratio = min(intersection_ratios)
            raise ValueError(
                f"Similarity threshold not met. A text has only {min_ratio:.2%} overlap with the others, but at least {self._similarity_threshold:.2%} is required. The texts are likely not the same."
            )

        aligned_texts = [[] for _ in texts]
        aligned_clean_texts = [[] for _ in clean_texts]
        # align_option=self._controller.get_align_option()
        #!DEBUG
        align_option = "union"
        #!END DEBUG

        # if align_option.lower() == "union":
        sentence_indices = [0]*len(clean_texts)
        while any(index < len(clean_text) for clean_text, index in zip(clean_texts, sentence_indices)):
            current_elements = get_current_elements()
            if any(index < 6 for index in sentence_indices):
                print(f"DEBUG {current_elements=}")
            if are_clean_sentences_similar(current_elements):
                indices_to_append = [(text_index, sentence_index)
                                     for text_index, sentence_index in enumerate(sentence_indices)]
                append_elements(indices_to_append)
                for i in range(len(sentence_indices)):
                    sentence_indices[i] += 1
                continue

            next_candidates = []  # List of tuples (sentence, text_index)

            # Check if sentence appears later in other texts
            buffers = [clean_text[index+1:index+self._max_lookahead]
                       for clean_text, index in zip(clean_texts, sentence_indices)]

            for text_index, sentence in enumerate(current_elements):
                if all(sentence not in buffer for buffer in buffers):
                    next_candidates.append((sentence, text_index))

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
