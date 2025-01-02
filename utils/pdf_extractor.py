

import os
import re
from typing import List
from PIL import Image
from pprint import pprint
from pymupdf import Rect, IRect
import pymupdf
from pathlib import Path


import time

#! for debug
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
#! end for debug


def measure_exec_time(func):
    """
    Decorator to measure the execution time of a function in milliseconds.

    Args:
        func (function): The function whose execution time is to be measured.

    Returns:
        function: The wrapped function with execution time measurement.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # High-precision timer
        result = func(*args, **kwargs)
        print(
            f"Execution time of {func.__name__}: {time.perf_counter() - start_time:.3f} seconds\n")
        return result
    return wrapper


class PDFExtractor:
    def __init__(self, pdf_path: str = "", pages_margins: str = None, pages: str = None, consider_bg_colors: bool = False, ignore_tables: bool = True, keep_headlines: bool = True):
        """
        Initializes the PDFExtractor with the given PDF path and various processing options.

        Args:
            pdf_path (str, optional): Path to the PDF file. Default is an empty string.
            consider_bg_colors (bool, optional): Whether to consider background colors during processing. Default is False.
            ignore_tables (bool, optional): Whether to ignore tables when extracting text. Default is True.
            keep_headlines (bool, optional): Whether to keep headlines when processing text. Default is False.
        """

        # Processing options
        # Whether to consider background colors in bounding box decisions
        self.consider_bg_colors = consider_bg_colors
        # Whether to ignore tables during text extraction
        self.ignore_tables = ignore_tables
        # Whether to ignore headlines during text extraction
        self.keep_headlines = keep_headlines

        # Background bounding box thresholds
        # Minimum area for considering a bounding box as part of the background
        self._min_area_for_background = 100
        # Minimum size (width or height) for considering a bounding box as part of the background
        self._min_size_for_background = 10

        # Text processing tolerances
        # Maximum vertical spacing between lines within the same text block
        self._max_line_vertical_spacing = 5
        # Tolerance for considering two text blocks to be left-aligned
        self._left_alignment_tolerance = 2
        # Vertical overlap tolerance (in pixels) for obstacles when extending bounding boxes
        self._vertical_overlap_tolerance = 3
        # Column gap tolerance (in pixels) for preventing merging across columns
        self._column_gap_tolerance = 1

        # Table detection
        # Maximum width for a box to be considered a vertical line (in pixels)
        self._max_width_for_vertical_line = 5
        # Minimum height for a box to be considered a vertical line (in pixels)
        self._min_height_for_vertical_line = 20
        # Tolerance for determining similar vertical position of lines or background_bboxes (in pixels)
        self._table_vertical_position_tolerance = 5
        # Tolerance for determining similar horizontal position of lines or background_bboxes (in pixels)
        self._table_horizontal_position_tolerance = 5
        # Minimum number of parallel vertical lines required to indicate a table
        self._min_parallel_lines_for_table = 3
        # Minimum number of background blocks in a row required to indicate a table
        self._min_table_rows = 2
        # Minimum number of background blocks in a colun required to indicate a table
        self._min_table_cols = 2

        # Headline detection
        # Min length for headlines
        self._min_headline_length = 8
        # most common font size
        self._most_common_fontsize = None
        # Maximum Number of regarded fonts (except headlinefonts)
        self._maximum_different_fonts = 1
        # store all font data associated with headlines
        self._toc_font_data = []
        # Max tolerance for headlines being smaller than normal text
        self.max_size_headline_tolerance = 1

        # Document-level data
        # Path to the currently loaded PDF file
        self.pdf_path = None
        # The PDF document object loaded with pymupdf
        self._doc = None
        # List of relevant pages
        self._relevant_pages = None
        # Margins for each page, specified as a list of lists [[left, top, right, bottom]]
        self._pages_margins = None
        # Default value vor not specified page margins
        self._default_margins = [10, 10, 10, 10]

        # Processed data
        self._document_content = []  # List storing extracted and processed data for each page
        # Formatted table of Content
        self._toc = None
        # Dictionary tracking the frequency of (clustered_font, normalized_font_size) combinations
        self._font_size_distribution = {}

        # Load the PDF document if a path is provided
        if pdf_path:
            self.load_document(
                pdf_path=pdf_path, pages_margins=pages_margins, pages=pages)

    @ measure_exec_time
    def load_document(self, pdf_path: str, pages_margins: list = None, pages: str = None) -> None:
        """
        Loads a new PDF document, initializes margins, extracts document data,
        and computes font clustering, font size normalization, and their distribution.

        Args:
            pdf_path (str): Path to the new PDF document.
            pages_margins (list, optional): Margins for each page, specified as a list of lists.
                                            Defaults to None, which applies a default margin to all pages.

        Raises:
            ValueError: If the length of `pages_margins` does not match the number of pages in the document.
        """
        # Load the document
        self.pdf_path = Path(pdf_path)
        self._doc = pymupdf.open(self.pdf_path)

        self._extract_clean_toc()
        self._initialize_pages_margins(pages_margins)
        self._initialize_relevant_pages(pages)
        self._extract_document()
        self.visualize_all_bboxes()
        self._accumulate_font_size_distribution()
        if self.keep_headlines:
            self._mark_headlines()
        self._filter_by_font_and_size()

    def _extract_clean_toc(self) -> None:
        """
        Extracts and processes the table of contents (TOC) from the document,
        formatting it for direct use in headline detection.

        The TOC is retrieved from self._doc, cleaned by removing digits, 
        whitespace, and special characters, and stored in self._toc as a list of 
        dictionaries with the keys 'text' and 'used'.

        Updates:
            - self._toc: List of dictionaries representing the cleaned TOC entries.
                        Each entry has the format:
                        [
                            {'text': 'chapterone', 'used': False},
                            {'text': 'introduction', 'used': False},
                            ...
                        ]
        """
        # Extract the raw TOC from the document
        raw_toc = self._doc.get_toc()

        # Process and clean each TOC entry
        self._toc = [
            {
                # Clean and normalize TOC title
                'text': re.sub(r'[\d\s\W_]+', '', entry[1]).lower(),
                'used': False
            }
            for entry in raw_toc
        ]

    def _initialize_pages_margins(self, pages_margins: str = None) -> None:
        """
        Initializes the page margins for the document.

        If `pages_margins` is provided as a string, it applies specific margin values
        to designated pages based on the string format "<pages>:<margins>;<pages>:<margins>".
        If no string is provided, all pages are initialized with the default margins.

        Args:
            pages_margins (str, optional): A string defining margins for specific pages.
                                        The format is "<pages>:<margins>", where <pages>
                                        can be individual page numbers or ranges, and
                                        <margins> can be a single value or four comma-separated values.
                                        Defaults to None.

        Raises:
            ValueError: If the format of the pages or margins is incorrect. Specific errors are raised for:
                        - Invalid page specification
                        - Incorrect margin format (not 1 or 4 values)
                        - Missing margin specification for given pages
        """
        # Initialize all pages with the default margins
        self._pages_margins = [self._default_margins] * len(self._doc)

        if not pages_margins:
            return

        # Process the string and apply custom margins
        margin_instructions = pages_margins.split(";")

        for instruction in margin_instructions:
            # Handle missing ":" error
            if ":" not in instruction:
                raise ValueError(
                    f"Missing margin specification for pages in '{instruction.strip()}'")

            pages_part, margins_part = map(str.strip, instruction.split(":"))

            # Validate that both parts are present
            if not pages_part or not margins_part:
                raise ValueError(
                    f"Incomplete instruction '{instruction.strip()}'. Both pages and margins must be specified.")

            # Parse page numbers
            page_numbers = set()
            for part in pages_part.split(","):
                part = part.strip()
                if '-' in part:
                    try:
                        start, end = map(int, part.split("-"))
                        if start > end:
                            raise ValueError(
                                f"Invalid page range '{part}' (start must be <= end).")
                        page_numbers.update(range(start, end + 1))
                    except ValueError:
                        raise ValueError(
                            f"Invalid page range format: '{part}'. Expected format 'start-end'.")
                else:
                    try:
                        page_numbers.add(int(part))
                    except ValueError:
                        raise ValueError(
                            f"Invalid page number '{part}'. Page numbers must be integers.")

            # Parse margins
            margins = list(map(str.strip, margins_part.split(",")))
            try:
                margins = list(map(int, margins))
            except ValueError:
                raise ValueError(
                    f"Invalid margin values '{margins_part}'. Margins must be integers.")

            if len(margins) not in {1, 4}:
                raise ValueError(
                    f"Invalid margin format '{margins_part}'. Must be 1 or 4 values.")

            if len(margins) == 1:
                margins = margins * 4  # Expand single value to [x, x, x, x]

            # Apply margins to the relevant pages
            for page in page_numbers:
                if 1 <= page <= len(self._doc):
                    self._pages_margins[page - 1] = margins
                else:
                    raise ValueError(
                        f"Page number '{page}' is out of document range (1-{len(self._doc)}).")

    def _initialize_relevant_pages(self, pages: str = None) -> None:
        """
        Initializes the relevant pages list by parsing a string of page ranges and individual pages.

        Args:
            pages (str, optional): A string describing page ranges and individual pages. Defaults to None.
        """
        if pages is None:
            self._relevant_pages = []
            return

        page_numbers = set()  # Use a set to avoid duplicates

        # Replace ; with , to standardize the delimiter
        parts = pages.replace(";", ",").split(",")

        for part in parts:
            if '-' in part:
                # Handle range, e.g., "6-11"
                start, end = part.split("-")
                page_numbers.update(range(int(start), int(end) + 1))
            else:
                # Handle single page entry
                page_numbers.add(int(part))

        # Sort and assign to the instance variable
        self._relevant_pages = sorted(page_numbers)

    def _extract_document(self) -> None:
        """
        Extracts content from each page of the document using the margins specified
        in the object variable `_pages_margins`, sorts the text data, and stores
        the results in an object variable.

        Raises:
            AttributeError: If `self.doc` or `_pages_margins` is not initialized.
            ValueError: If the number of margins in `_pages_margins` does not match
                        the number of pages in the document.
        """
        if not hasattr(self, "_doc"):
            raise AttributeError(
                "The document object 'self._doc' is not initialized.")

        if not hasattr(self, "_pages_margins"):
            raise AttributeError(
                "The variable '_pages_margins' is not initialized.")

        if not hasattr(self, "_relevant_pages"):
            raise AttributeError(
                "The variable '_relevant_pages' is not initialized.")

        # Validate that the number of margin entries matches the number of pages
        if len(self._pages_margins) != len(self._doc):
            raise ValueError(
                "The number of margins in '_pages_margins' must match the number of pages in the document.")

        self._document_content = []

        if self._relevant_pages:
            self._doc = [self._doc[i-1] for i in self._relevant_pages]
            self._pages_margins = [self._pages_margins[i-1]
                                   for i in self._relevant_pages]

        for page, page_margins in zip(self._doc, self._pages_margins):
            page_content = self._extract_page_content(page, page_margins)
            page_content = self._sort_text_data(page_content)
            self._document_content.append(page_content)

    def _accumulate_font_size_distribution(self) -> None:
        """
        Accumulates the total character counts for each combination of 
        clustered font and normalized font size across all pages.

        Updates:
            - self._font_size_distribution: A dictionary mapping 
            (clustered_font, normalized_font_size) to the cumulative character count.
        """

        # Initialize the cumulative font size distribution
        self._font_size_distribution = {}

        # Normalize and aggregate font size distribution
        for page_content in self._document_content:
            page_font_distribution = page_content.get(
                "font_and_size_distribution", {})

            for key, count in page_font_distribution.items():
                self._font_size_distribution[key] = self._font_size_distribution.get(
                    key, 0) + count

        # Set the most common fontsize
        self._most_common_fontsize = max(
            self._font_size_distribution, key=lambda x: self._font_size_distribution[x])[1]

    def _mark_headlines(self) -> None:
        """
        Marks potential headlines by checking each line, blocks of lines, and consecutive lines 
        with matching font_data against the table of contents (TOC).

        The method performs three levels of checks to identify headlines:
        1. Individual line check.
        2. Block-level check (combining all lines in a text block).
        3. Consecutive line check for lines with the same font_data.

        Updates:
            - Each line is marked with the key 'headline' set to True if it is recognized as a headline, 
            otherwise False.
        """
        for page in self._document_content:
            for text_block in page.get("text_data", ([], []))[0]:

                # Step 1: Check each individual line for headline match
                for line in text_block.get("lines", []):
                    line["text"] = " ".join(span.get("text", "").strip()
                                            for span in line.get("spans", []))
                    if self._is_headline(line):
                        line["headline"] = True
                    else:
                        line["headline"] = False

                # Step 2: Check entire text block by combining all lines
                combined_block_text = " ".join(
                    line["text"] for line in text_block.get("lines", [])
                ).strip()

                if combined_block_text:
                    combined_line_data = {
                        "text": combined_block_text,
                        "font_data": text_block.get("font_data", (None, 0))
                    }
                    if self._is_headline(combined_line_data):
                        # Mark all lines in the block as headline
                        for line in text_block.get("lines", []):
                            line["headline"] = True
                        continue  # Skip further checks if block-level headline is found

                # Step 3: Check consecutive lines with the same font_data
                consecutive_lines = []
                previous_font_data = None

                for line in text_block.get("lines", []):
                    if line["headline"]:
                        # Skip already marked headlines
                        continue

                    current_font_data = line.get("font_data", (None, 0))

                    # Check if the line's font_data matches the previous one
                    if current_font_data == previous_font_data:
                        consecutive_lines.append(line)
                    else:
                        # If new font_data is encountered, process the accumulated lines
                        if len(consecutive_lines) > 1:
                            combined_text = " ".join(
                                l["text"] for l in consecutive_lines).strip()
                            combined_data = {
                                "text": combined_text,
                                "font_data": current_font_data
                            }
                            if self._is_headline(combined_data):
                                for l in consecutive_lines:
                                    l["headline"] = True

                        # Reset the consecutive list and start tracking the new line
                        consecutive_lines = [line]
                        previous_font_data = current_font_data

                # Final check for remaining consecutive lines at the end of the block
                if len(consecutive_lines) > 1:
                    combined_text = " ".join(l["text"]
                                             for l in consecutive_lines).strip()
                    combined_data = {
                        "text": combined_text,
                        "font_data": previous_font_data
                    }
                    if self._is_headline(combined_data):
                        for l in consecutive_lines:
                            l["headline"] = True

    def _filter_by_font_and_size(self) -> None:
        """
        Filters the font size distribution to retain entries with the highest frequency,
        ensuring that no more than the specified number of different fonts are selected.

        Updates:
            - self._document_content: The page content is filtered such that only text blocks
                                    and lines with the selected fonts and sizes are retained.
        """

        # Sort font size distribution by frequency (value) in descending order
        sorted_distribution = sorted(
            self._font_size_distribution.items(), key=lambda x: x[1], reverse=True)

        selected_fonts = []
        selected_fonts_set = set()  # For faster lookup

        # Select entries until the desired number of different fonts is reached
        for font_data, count in sorted_distribution:
            if font_data not in selected_fonts_set:
                selected_fonts_set.add(font_data)

            if len(selected_fonts_set) == self._maximum_different_fonts:
                break

        selected_fonts = list(selected_fonts_set)

        # Filter page content based on selected fonts and sizes
        for page_content in self._document_content:
            filtered_text_blocks = []
            filtered_text_bboxes = []

            for block, bbox in zip(page_content["text_data"][0], page_content["text_data"][1]):
                filtered_lines = [
                    line for line in block.get("lines", [])
                    if (line.get("font_data") in selected_fonts or line["headline"])
                ]

                if filtered_lines:
                    block["lines"] = filtered_lines
                    filtered_text_blocks.append(block)
                    filtered_text_bboxes.append(bbox)

            # Update the page with filtered text blocks and bounding boxes
            page_content["text_data"] = (
                filtered_text_blocks, filtered_text_bboxes)

    def _find_connected_text_boxes(self, page_content):
        """
        Finds connected text boxes on a page, considering margins and optional background colors.

        Args:
            page: The page object to analyze.
            consider_bg_colors (bool): Whether to consider background colors in the analysis.
        """
        page_content = self._sort_text_data(page_content)
        page_content = self._extend_bounding_boxes(page_content)
        page_content = self._sort_text_data(page_content)
        page_content = self._merge_text_boxes(page_content)
        # self.visualize_bboxes(page, page_content)

    def _extract_page_content(self, page: pymupdf.Page, page_margins: list[int]) -> dict:
        """
        Extracts and processes content from a PDF page within specified margins.

        This method clips the page based on the provided margins, extracts text blocks, images, 
        and graphical elements, and filters them based on their position and relevance. It also 
        computes the distribution of fonts and font sizes across the page and annotates each line 
        with the most frequent font and size combination.

        Args:
            page (pymupdf.Page): The PDF page to extract content from.
            page_margins (list[int]): A list of four integers representing margins in the order 
                                    [left, top, right, bottom]. These margins define the area 
                                    of the page to process.

        Returns:
            dict: A dictionary containing the extracted and filtered content from the page. The 
                dictionary is structured as follows:

                {
                    "geometry": pymupdf.Rect,
                        - A rectangle representing the clipped region of the page based on the margins.

                    "text_data": (list, list),
                        - A tuple consisting of:
                            1. A list of filtered text blocks (dicts) that contain "lines" and 
                                "spans" with associated text and font information. 
                                Each **line** within a block may include the key `font_data`, 
                                indicating the dominant font and size combination for that line. 
                                Example:
                                {
                                    "lines": [
                                        {
                                            "spans": [...],
                                            "font_data": ('ArialMT', 10.0)
                                        }
                                    ]
                                }
                            2. A list of bounding boxes (irect format) for the text blocks.

                    "obstacles": list,
                        - A list of bounding boxes (irect format) representing elements that could 
                            obstruct text or indicate table structures. This includes:
                            * Non-horizontal text
                            * Table bounding boxes
                            * Images
                            * Graphics
                            * (Optional) Background graphics if self.consider_bg_colors is enabled

                    "backgrounds": list,
                        - A list of bounding boxes (irect format) representing background graphics 
                            that exceed the minimum size or area thresholds.

                    "font_and_size_distribution": dict,
                        - A dictionary mapping tuples of (clustered_font, normalized_font_size) 
                            to the total character count for that font and size across the page.
                            Example:
                            {
                                ('ArialMT', 10.0): 125,
                                ('TimesNewRoman', 12.0): 400
                            }
                }
        """
        # Geometry data
        clip_rect = Rect(page_margins[0], page_margins[1], page.rect.width -
                         page_margins[2], page.rect.height - page_margins[3])

        # Extract text blocks
        text_blocks = page.get_text("dict", clip=clip_rect)["blocks"]

        # Early return for empty pages
        if not text_blocks:
            return {
                "geometry": clip_rect,
                "text_data": ([], []),
                "obstacles": [],
                "backgrounds": [],
                "font_and_size_distribution": {},
            }

        # Initialize variables
        font_and_size_distribution = {}
        clusters = {}

        # Extract images
        images = page.get_images()
        image_bboxes = [page.get_image_rects(
            image)[0].irect for image in images]
        # Extract graphics
        graphics = page.get_drawings()
        graphic_bboxes = [graphic["rect"].irect for graphic in graphics]

        # Initialize lists for background, filtered graphics, and vertical lines
        background_bboxes = []
        filtered_graphic_bboxes = []
        vertical_lines = []

        # Classify graphics into background, filtered graphics, and vertical lines
        for bbox in graphic_bboxes:
            bbox_width = bbox.width
            bbox_height = bbox.height

            # Check for background graphics
            if bbox_width * bbox_height > self._min_area_for_background and min(bbox_width, bbox_height) > self._min_size_for_background:
                background_bboxes.append(bbox)
                continue
            else:
                filtered_graphic_bboxes.append(bbox)

            # Check for vertical lines using absolute pixel tolerances
            if bbox_width <= self._max_width_for_vertical_line and bbox_height >= self._min_height_for_vertical_line:
                vertical_lines.append(bbox)

        graphic_bboxes = list(set(filtered_graphic_bboxes))
        background_bboxes = list(set(background_bboxes))
        vertical_lines = list(set(vertical_lines))

        # Check for potential tables
        potential_table = self._are_tables_on_page(
            vertical_lines, background_bboxes)

        # Extract tables
        if potential_table:
            tables = page.find_tables()
            table_bboxes = [Rect(table.bbox).irect for table in tables]
        else:
            table_bboxes = []

        # Text blocks
        text_bboxes = []
        non_horizontal_text_bboxes = []
        filtered_text_blocks = []

        for block in text_blocks:
            if not block.get("lines", []):
                continue

            # Filter non-horizontal text
            if block["lines"][0]["dir"] != (1.0, 0.0):
                non_horizontal_text_bboxes.append(Rect(block["bbox"]).irect)
                continue

            text_bbox = Rect(block["bbox"]).irect
            # Skip the block if it is within a detected image
            if image_bboxes and any(self._is_bbox_within(text_bbox, image_bbox) for image_bbox in image_bboxes):
                continue

            # Skip the block if it is within a detected graphic
            if graphic_bboxes and any(self._is_bbox_within(text_bbox, graphic_bbox) for graphic_bbox in graphic_bboxes):
                continue

            # Skip the block if it is within a detected table
            if table_bboxes and any(self._is_bbox_within(text_bbox, table_bbox) for table_bbox in table_bboxes):
                continue

            # Textblock is relevant
            filtered_text_blocks.append(block)

            # Process spans for font and size distribution
            for line in block.get("lines", []):
                line_font_distribution = {}

                for span in line.get("spans", []):
                    font_name = span.get("font", None)
                    font_size = span.get("size", None)
                    if font_name is None or font_size is None:
                        continue

                    # process font data
                    clustered_font = self._cluster_span_font(
                        font_name, clusters)
                    normalized_font_size = round(font_size * 2, 0) / 2
                    font_data = (clustered_font, normalized_font_size)

                    # Count occurences
                    char_count = len(span.get("text", "").strip())

                    # Accumulate counts for each (font, size) pair
                    line_font_distribution[font_data] = line_font_distribution.get(
                        font_data, 0) + char_count
                    font_and_size_distribution[font_data] = font_and_size_distribution.get(
                        font_data, 0) + char_count

                # Determine the most frequent (font, size) pair in the line
                if not line_font_distribution:
                    continue

                dominant_font_data = max(
                    line_font_distribution.items(), key=lambda x: x[1])[0]
                line["font_data"] = dominant_font_data

            # Combine lines within blocks into bounding boxes
            # Use the first line's bbox as initial rect
            initial_rect = list(block["lines"][0]["bbox"])
            for line in block["lines"]:
                # Check for non-empty text spans
                if any(span["text"].strip() for span in line["spans"]):
                    line_bbox = line["bbox"]
                    initial_rect[0] = min(initial_rect[0], line_bbox[0])
                    initial_rect[1] = min(initial_rect[1], line_bbox[1])
                    initial_rect[2] = max(initial_rect[2], line_bbox[2])
                    initial_rect[3] = max(initial_rect[3], line_bbox[3])
            text_bboxes.append(Rect(initial_rect).irect)

        # Obstacle boxes
        obstacle_bboxes = non_horizontal_text_bboxes + \
            table_bboxes + image_bboxes + graphic_bboxes
        if self.consider_bg_colors:
            obstacle_bboxes += background_bboxes

        page_content = {
            "geometry": clip_rect,
            "text_data": (filtered_text_blocks, text_bboxes),
            "obstacles": obstacle_bboxes,
            "backgrounds": background_bboxes,
            "font_and_size_distribution": font_and_size_distribution,
        }
        return page_content

    def _cluster_span_font(self, font_name: str, clusters: dict) -> str:
        """
        Clusters a given font name based on its root and updates the clusters dictionary.

        Args:
            font_name (str): The font name to be clustered.
            clusters (dict): Dictionary of existing font clusters, where the key is the font name
                            and the value is its clustered root.

        Returns:
            str: The clustered font name.
        """
        if font_name in clusters:
            return clusters[font_name]

        # Extract the root of the font name
        match = re.match(r'([A-Za-z][A-Za-z]+)', font_name)
        root = match.group(1) if match else font_name
        clusters[font_name] = root
        return root

    def _are_tables_on_page(self, vertical_lines: List[IRect], background_bboxes: List[IRect]) -> bool:
        # # Check for parallel vertical lines of similar length
        if vertical_lines and len(vertical_lines) >= self._min_parallel_lines_for_table:
            # Compare lines to find similar lengths
            for i in range(len(vertical_lines)-1):
                same_vertical_position_count = 1
                line = vertical_lines[i]
                for j in range(i+1, len(vertical_lines)):
                    other_line = vertical_lines[j]
                    if abs(line.y0-other_line.y0) <= self._table_vertical_position_tolerance and abs(line.y1-other_line.y1) <= self._table_vertical_position_tolerance:
                        same_vertical_position_count += 1
                    if same_vertical_position_count >= self._min_parallel_lines_for_table:
                        return True

        # todo testtables needed
        if background_bboxes and len(background_bboxes) >= self._min_table_cols*self._min_table_rows:
            # Find rows
            rows = []
            background_bboxes.sort(
                key=lambda background_bbox: background_bbox.y0)

            first_bbox = background_bboxes[0]
            row = [first_bbox]
            for background_bbox in background_bboxes[1:]:
                if self._are_in_row(first_bbox, background_bbox):
                    row.append(background_bbox)
                else:
                    if len(row) >= self._min_table_cols:
                        rows.append(row)
                    first_bbox = background_bbox
                    row = [first_bbox]

            if len(rows) < self._min_table_rows:
                return False

            # Group rows to potential tables
            potential_tables = []
            potential_table = [rows[0]]
            for i in range(len(rows)-1):
                # Check is rows are directly consecutive
                if abs(rows[i][0].y1-rows[i+1][0].y0) <= self._table_vertical_position_tolerance and len(rows[i]) == len(rows[i+1]):
                    potential_table.append(rows[i+1])
                else:
                    # Ensure that potential table has sufficient number of rows
                    if len(potential_table) >= self._min_table_rows:
                        potential_tables.append(potential_table)
                    potential_table = [rows[i+1]]

            if not potential_tables:
                return False

            # Check if cols in potential tables are aligned
            tables = []

            for potential_table in potential_tables:
                first_row = potential_table[0]
                table = [first_row]
                for row in rows[1:]:
                    # Check if all cols are aligned for pair of rows
                    if all(self._are_in_col(bbox1, bbox2) for bbox1, bbox2 in zip(first_row, row)):
                        table.append(row)
                    else:
                        if len(table) >= self._min_table_rows:
                            tables.append(table)
                        table = [row]
            return len(tables) > 0

            # def _extract_page_content(self, page: pymupdf.Page, page_margins: list[int]) -> dict:
            #     """
            #     Extracts content from a PDF page within the specified margins and organizes it into
            #     geometric data, text blocks, and obstacle information.

            #     Args:
            #         page (pymupdf.Page): The page object to extract content from.
            #         page_margins (list[int]): A list of integers specifying margins (left, top, right, bottom)
            #                                 for clipping the page content.

            #     Returns:
            #         dict: A dictionary containing the following keys:
            #             - "geometry" (Rect): The rectangular area used for clipping the content.
            #             - "text_data" (tuple): A tuple containing:
            #                 * A list of dictionaries representing text blocks within the clipped area.
            #                 * A list of Rect objects representing the bounding boxes of the text blocks.
            #             - "obstacles" (list[Rect]): A list of Rect objects representing obstacles
            #                                         such as non-horizontal text, tables, images, and graphics.
            #             - "backgrounds" (list[Rect]): A list of Rect objects representing background graphics
            #                                         meeting the specified size and area criteria.
            #     """
            #     # geometric data
            #     left = page_margins[0]
            #     top = page_margins[1]
            #     right = page.rect.width - page_margins[2]
            #     bottom = page.rect.height - page_margins[3]
            #     clip_rect = Rect(left, top, right, bottom)

            #     # Get text blocks within clipped area
            #     text_blocks = page.get_text("dict", clip=clip_rect)["blocks"]

            #     # If no text found on this page
            #     if not text_blocks:
            #         {
            #             "geometry": clip_rect,
            #             "text_data": ([{"font_name": "", "lines": []}], []),
            #             "obstacles": [],
            #             "backgrounds": [],
            #         }

            #     # Separate horizontal and non-horizontal text blocks in one pass
            #     non_horizontal_text_bboxes = []
            #     filtered_text_blocks = []

            #     for block in text_blocks:
            #         if block.get("lines") and len(block["lines"]) > 0 and block["lines"][0]["dir"] != (1.0, 0.0):
            #             non_horizontal_text_bboxes.append(Rect(block["bbox"]).irect)
            #         else:
            #             filtered_text_blocks.append(block)

            #     # Update text_blocks to only contain horizontal text blocks
            #     text_blocks = filtered_text_blocks

            #     # Find table, image, and graphic boxes
            #     tables = page.find_tables()
            #     table_bboxes = [Rect(table.bbox).irect for table in tables]

            #     images = page.get_images()
            #     image_bboxes = [page.get_image_rects(
            #         image)[0].irect for image in images]

            #     graphics = page.get_drawings()
            #     graphic_bboxes = [graphic["rect"].irect for graphic in graphics]

            #     background_bboxes = []
            #     filtered_graphic_bboxes = []

            #     for box in graphic_bboxes:
            #         if box.width * box.height > self._min_area_for_background and min(box.width, box.height) > self._min_size_for_background:
            #             background_bboxes.append(box)
            #         else:
            #             filtered_graphic_bboxes.append(box)

            #     graphic_bboxes = filtered_graphic_bboxes

            #     obstacle_bboxes = non_horizontal_text_bboxes + \
            #         table_bboxes+image_bboxes+graphic_bboxes
            #     if self.consider_bg_colors:
            #         obstacle_bboxes += background_bboxes

            #     # Ignore tables
            #     if self.ignore_tables:
            #         text_blocks = [block for block in text_blocks if not any(
            #             self._is_bbox_within(Rect(block["bbox"]).irect, table_bbox) for table_bbox in table_bboxes)]

            #     # Combine lines within blocks into bounding boxes
            #     text_bboxes = []
            #     for block in text_blocks:
            #         # Skip blocks without "lines" or empty "lines" lists
            #         if not block.get("lines") or len(block["lines"]) == 0:
            #             continue

            #         # Use the first line's bbox as initial rect
            #         initial_rect = list(block["lines"][0]["bbox"])
            #         for line in block["lines"]:
            #             # Check for non-empty text spans
            #             if any(span["text"].strip() for span in line["spans"]):
            #                 line_bbox = line["bbox"]
            #                 initial_rect[0] = min(initial_rect[0], line_bbox[0])
            #                 initial_rect[1] = min(initial_rect[1], line_bbox[1])
            #                 initial_rect[2] = max(initial_rect[2], line_bbox[2])
            #                 initial_rect[3] = max(initial_rect[3], line_bbox[3])
            #         text_bboxes.append(Rect(initial_rect).irect)

            #     return {
            #         "geometry": clip_rect,
            #         "text_data": (text_blocks, text_bboxes),
            #         "obstacles": obstacle_bboxes,
            #         "backgrounds": background_bboxes,
            #     }

    def _is_headline(self, line_data: dict) -> bool:
        """
        Determines if a given text is a headline by checking against the preprocessed table of contents (TOC).

        This method verifies if the text is long enough, matches an entry in the TOC (ignoring numbers,
        whitespaces, and special characters), and is written in a sufficiently large font.

        Args:
            line (dict): The line text to be checked.

        Returns:
            bool: True if the text matches an entry in the TOC and meets the length and font size criteria, 
                False otherwise.
        """

        text = line_data["text"]
        print(text)
        font_size = line_data["font_data"][1]
        # Guard clause: Check if TOC exists
        if not self._toc:
            return False
        print("Toc yes")

        if text == "Regionale Grundwasserverhältnisse":
            print(f"\n{len(text)=}")
            print(f"{self._min_headline_length=}\n")
        # Guard clause: Check minimum length
        if len(text) < self._min_headline_length:
            return False
        print("len yes")

        # Clean the input text by removing digits, whitespaces, and special characters
        clean_text = re.sub(r'[\d\s\W_]+', '', text).lower()

        if text == "Regionale Grundwasserverhältnisse":
            print(f"\n{font_size=}")
            print(f"{self._most_common_fontsize=}\n")
        # Guard clause: Check minimum font size
        if font_size < self._most_common_fontsize-self.max_size_headline_tolerance:
            return False
        print("fontsize yes")

        print(f"{clean_text=}\n")
        # Compare the cleaned text with preprocessed TOC entries
        for toc_entry in self._toc:
            if clean_text == toc_entry["text"] and not toc_entry["used"]:
                toc_entry["used"] = True  # Mark TOC entry as used
                print(f"Headline: {text}")
                return True

        print("No Entry in toc")
        return False

    def _extend_bounding_boxes(self, page_content: dict) -> dict:
        """
        Extends the text bounding boxes within the page_content dictionary to the right edge of the page,
        stopping at obstacles and adjusting for columns.

        Args:
            page_content (dict): A dictionary containing page data including 'text_data', 'obstacles', and 'backgrounds'.

        Returns:
            dict: The updated page_content dictionary with extended and sorted 'text_data'.
        """
        text_blocks, text_bboxes = page_content["text_data"]
        obstacle_bboxes = page_content["obstacles"]

        # Extend text bounding boxes to the right edge of the page, stopping at obstacles
        for index, text_bbox in enumerate(text_bboxes):
            # Start by extending the box to the right edge of the page
            extended_bbox = Rect(text_bbox.x0, text_bbox.y0,
                                 page_content["geometry"].x1, text_bbox.y1).irect

            # Check for collisions with obstacles
            for obstacle_bbox in obstacle_bboxes:
                if extended_bbox.intersects(obstacle_bbox):
                    # Calculate the vertical overlap
                    overlap_top = max(0, obstacle_bbox.y1 - extended_bbox.y0)
                    overlap_bottom = max(
                        0, extended_bbox.y1 - obstacle_bbox.y0)

                    # Ignore the obstacle if overlap is within the vertical overlap tolerance
                    if overlap_top > self._vertical_overlap_tolerance and overlap_bottom > self._vertical_overlap_tolerance:
                        extended_bbox.x1 = min(
                            extended_bbox.x1, obstacle_bbox.x0)

            # Prevent merging across columns
            for other_bbox in text_bboxes:
                if other_bbox == text_bbox:  # Skip the current box
                    continue
                # Check if other box is to the right with a positive gap
                if other_bbox.x0 > text_bbox.x1 + self._column_gap_tolerance:
                    # Adjust the right edge
                    extended_bbox.x1 = min(extended_bbox.x1, other_bbox.x0)

            # Update the bounding box
            text_bboxes[index] = extended_bbox

        # Update text_data in the page_content dictionary
        page_content["text_data"] = (text_blocks, text_bboxes)

        return page_content

    def _merge_text_boxes(self, page_content: dict) -> dict:
        """
        Merges close or overlapping text blocks within the page_content dictionary.

        Args:
            page_content (dict): A dictionary containing page data including 'text_data'.

        Returns:
            dict: The updated page_content dictionary with merged 'text_data'.
        """
        text_blocks, text_bboxes = page_content["text_data"]

        # Initialize merged lists with the first block and bounding box
        merged_text_blocks = [text_blocks[0]]
        merged_text_bboxes = [text_bboxes[0]]

        # Iterate over the remaining blocks and bounding boxes
        for block, text_bbox in zip(text_blocks[1:], text_bboxes[1:]):
            # Get the last merged bounding box
            last_text_bbox = merged_text_bboxes[-1]

            # Check if the rectangles intersect or are left-aligned with a small horizontal gap
            intersects = text_bbox.intersects(last_text_bbox)
            horizontal_gap = abs(text_bbox.y0 - last_text_bbox.y1)

            # Check alignment and gap
            left_alignment = abs(
                text_bbox.x0 - last_text_bbox.x0) <= self._left_alignment_tolerance
            within_max_spacing = horizontal_gap <= self._max_line_vertical_spacing

            # Merge condition: rectangles intersect or are left-aligned and within spacing
            if intersects or (left_alignment and within_max_spacing):
                # Merge the bounding box
                merged_bbox = Rect(
                    min(last_text_bbox.x0, text_bbox.x0),
                    min(last_text_bbox.y0, text_bbox.y0),
                    max(last_text_bbox.x1, text_bbox.x1),
                    max(last_text_bbox.y1, text_bbox.y1),
                )
                merged_text_bboxes[-1] = merged_bbox  # Update the last bbox
                # Merge lines
                merged_text_blocks[-1]["lines"].extend(block["lines"])
            else:
                # Add as a new separate block and bbox
                merged_text_blocks.append(block)
                merged_text_bboxes.append(text_bbox)

        # Update page_content with merged text data
        page_content["text_data"] = (merged_text_blocks, merged_text_bboxes)

        return page_content

    def _sort_text_data(self, page_content: dict) -> dict:
        """
        Sorts the text data (text_blocks and text_bboxes) within the page_content dictionary
        and updates the dictionary with the sorted data.

        Args:
            page_content (dict): A dictionary containing page data including 'text_data' and 'backgrounds'.

        Returns:
            dict: The updated page_content dictionary with sorted 'text_data'.
        """
        text_blocks, text_bboxes = page_content["text_data"]
        background_bboxes = page_content["backgrounds"]

        # Combine text_blocks and text_bboxes for sorting
        combined = list(zip(text_blocks, text_bboxes))
        if self.consider_bg_colors:
            with_bg_color = [item for item in combined if self._has_bg_color(
                item[1], background_bboxes)]
            without_bg_color = [item for item in combined if not self._has_bg_color(
                item[1], background_bboxes)]
            without_bg_color.sort(key=lambda x: (x[1].x0, x[1].y0))
            with_bg_color.sort(key=lambda x: (x[1].x0, x[1].y0))
            combined = without_bg_color + with_bg_color
        else:
            combined.sort(key=lambda x: (x[1].x0, x[1].y0))

        # Unzip the sorted combined list back into text_blocks and text_bboxes
        page_content["text_data"] = list(map(
            list, zip(*combined))) if combined else ([], [])

        return page_content

    def _is_bbox_within(self, inner_bbox, outer_bbox):
        """
        Checks if one bounding box is within another.

        Args:
            inner_bbox (Rect): The inner bounding box.
            outer_bbox (Rect): The outer bounding box.

        Returns:
            bool: True if inner_bbox is within outer_bbox.
        """
        return (
            inner_bbox.x0 >= outer_bbox.x0
            and inner_bbox.y0 >= outer_bbox.y0
            and inner_bbox.x1 <= outer_bbox.x1
            and inner_bbox.y1 <= outer_bbox.y1
        )

    def _are_in_row(self, bbox: IRect, other_bbox: IRect) -> bool:
        """
        Checks if two bounding boxes are within the same row.

        Args:
            bbox (IRect): The first bounding box to compare.
            other_bbox (IRect): The second bounding box to compare.

        Returns:
            bool: True if the two bounding boxes are within the same row based on vertical position tolerance,
                False otherwise.
        """
        return (
            abs(bbox.y0 - other_bbox.y0) <= self._table_vertical_position_tolerance
            and abs(bbox.y1 - other_bbox.y1) <= self._table_vertical_position_tolerance
        )

    def _are_in_col(self, bbox: IRect, other_bbox: IRect) -> bool:
        """
        Checks if two bounding boxes are within the same column.

        Args:
            bbox (IRect): The first bounding box to compare.
            other_bbox (IRect): The second bounding box to compare.

        Returns:
            bool: True if the two bounding boxes are within the same column based on horizontal position tolerance,
                False otherwise.
        """
        return (
            abs(bbox.x0 - other_bbox.x0) <= self._table_horizontal_position_tolerance
            and abs(bbox.x1 - other_bbox.x1) <= self._table_horizontal_position_tolerance
        )

    def _has_bg_color(self, bbox, background_bboxes):
        """
        Checks if a bounding box has a background color.

        Args:
            bbox (Rect): The bounding box to check.
            background_bboxes (list[Rect]): List of background bounding boxes.

        Returns:
            bool: True if the bbox has a background color.
        """
        return any(self._is_bbox_within(bbox, bg_bbox) for bg_bbox in background_bboxes)

    #!just for debugging

    def visualize_bboxes(self, page, page_content: dict, store: bool = False) -> None:
        """
        Visualizes bounding boxes on the given page by drawing rectangles and writing the index
        of each box in its center.

        Args:
            page (Page): The PyMuPDF page object to annotate.
            page_content (dict): A dictionary containing page data including 'text_data' and 'obstacles'.
        """
        text_bboxes = page_content["text_data"][1]  # Extract text_bboxes from text_data
        obstacle_bboxes = page_content["obstacles"]

        # Create a shape object for drawing text_boxes
        shape = page.new_shape()

        for index, bbox in enumerate(text_bboxes):
            # Draw the bounding box in red
            shape.draw_rect(bbox)

            # Write the index number (+1) in the center of the box
            center_x = (bbox.x0 + bbox.x1) / 2
            center_y = (bbox.y0 + bbox.y1) / 2
            shape.insert_text((center_x, center_y), str(
                index + 1), fontsize=20, color=(1, 0, 0))

        # Commit the drawings to the page
        shape.finish(color=(1, 0, 0), fill=None, width=1)
        shape.commit()

        # Create a shape object for drawing obstacles
        shape = page.new_shape()

        for index, bbox in enumerate(obstacle_bboxes):
            # Draw the bounding box in green
            shape.draw_rect(bbox)

            # Write the index number (+1) in the center of the box
            center_x = (bbox.x0 + bbox.x1) / 2
            center_y = (bbox.y0 + bbox.y1) / 2
            shape.insert_text((center_x, center_y), str(
                index + 1), fontsize=20, color=(0, 1, 0))

        # Commit the drawings to the page
        shape.finish(color=(0, 1, 0), fill=None, width=1)
        shape.commit()

        # Render the page as a pixmap
        pix = page.get_pixmap()

        # Convert the pixmap to a Pillow image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        if store:
            # Ensure the directory exists
            output_dir = "test_img"
            os.makedirs(output_dir, exist_ok=True)

            # Define the output file path
            output_path = os.path.join(
                output_dir, f"page_{page.number + 1}.png")

            # Save the image
            img.save(output_path)

            return

        # Show the image using Pillow
        img.show()

    def visualize_all_bboxes(self) -> None:
        for index, page in enumerate(self._doc):
            page_content = self._document_content[index]
            self.visualize_bboxes(
                page=page, page_content=page_content, store=True)


# Example usage:
if __name__ == "__main__":

    test_pdf_path = "test_data/pdf"
    test_docs = [
        "Grundwasser-Überwachungsprogramm - 2022.pdf",
        "Auf zu neuen Wegen – gemeinschaftlich und nachhaltig wirtschaften!_2022.pdf",
        "10274-Sondermessungen_2020_Abschlussbericht.pdf",
        "Energie-_und_Stoffstrommanagement._Praxisbeispiel_Kunststofflackierung.pdf",
    ]
    DOCUMENT = 0
    margins = [10, 10, 10, 10]
    pages = "6-36"
    pdf_extractor = PDFExtractor(
        pdf_path=f"{test_pdf_path}/{test_docs[DOCUMENT]}", pages=pages)
    # for index, page in enumerate(pdf_extractor._doc):
    #     page_content = pdf_extractor._document_content[index]
    #     pdf_extractor.visualize_bboxes(
    #         page=page, page_content=page_content, store=True)

    # TEST_PAGE = 14
    # page = pdf_extractor.doc[TEST_PAGE-1]
    # page_content = pdf_extractor._document_content[TEST_PAGE-1]
    # pdf_extractor.visualize_bboxes(page=page, page_content=page_content)
    # obstacle = page_content["obstacles"][20]
    # pdf_extractor._find_connected_text_boxes(page, margins)

    # def _cluster_and_normalize_fonts(self, page_content: dict) -> dict:
    #     """
    #     Analyzes font data (clustering and size normalization) for all spans in the page_content dictionary.

    #     This method clusters fonts and normalizes font sizes, combining the responsibilities of
    #     two separate tasks into one for performance reasons.

    #     Args:
    #         page_content (dict): A dictionary containing page data, including 'text_data'.

    #     Returns:
    #         dict: The updated page_content dictionary with font clustering and normalized font size
    #             information added to each span.
    #     """
    #     text_blocks = page_content["text_data"][0]  # Extract text_blocks from page_content

    #     # Ensure max_font_size and min_font_size are set as object variables
    #     if not hasattr(self, "_max_font_size") or not hasattr(self, "_min_font_size"):
    #         raise AttributeError(
    #             "Object variables '_max_font_size' and '_min_font_size' must be set before calling this method."
    #         )

    #     # Calculate font size range
    #     font_size_range = self._max_font_size - self._min_font_size

    #     # Initialize font clusters
    #     font_list = []
    #     for block in text_blocks:
    #         for line in block.get("lines", []):
    #             for span in line.get("spans", []):
    #                 if "font" in span:
    #                     font_list.append(span["font"])
    #     font_list = list(set(font_list))  # Remove duplicates

    #     # Generate font clusters
    #     clusters = {}
    #     def find_shortest_word(word_list): return min(word_list, key=len)

    #     def find_root(word):
    #         match = re.match(r'([A-Za-z][A-Za-z]+)', word)
    #         return match.group(1) if match else word

    #     while font_list:
    #         shortest_word = find_shortest_word(font_list)
    #         root = find_root(shortest_word)
    #         for word in font_list.copy():
    #             if root in word:
    #                 clusters[word] = root
    #                 font_list.remove(word)

    #     # Process spans: Normalize font sizes and cluster fonts
    #     for block in text_blocks:
    #         for line in block.get("lines", []):
    #             for span in line.get("spans", []):
    #                 # Normalize font size
    #                 if "size" in span:
    #                     normalized_size = round(
    #                         (span["size"] - self._min_font_size) /
    #                         font_size_range, 2
    #                     )
    #                     span["normalized_font_size"] = normalized_size
    #                 # Apply font clustering
    #                 if "font" in span and span["font"] in clusters:
    #                     span["font_cluster"] = clusters[span["font"]]

    #     # Update the page_content dictionary with the modified text blocks
    #     page_content["text_data"] = (text_blocks, page_content["text_data"][1])

    #     return page_content

    # def _cluster_fonts(self, page_content: dict) -> dict:
    #     """
    #     Clusters fonts found in spans and updates the spans to reflect font families.

    #     This method lists all occurring fonts from the spans, creates a dictionary mapping
    #     individual fonts to their stems, and updates the spans to use these stems. This aids
    #     in the identification of headings by normalizing font variations.

    #     Args:
    #         page_content (dict): A dictionary containing page data, including 'text_data'.

    #     Returns:
    #         dict: The updated page_content dictionary with font clusters added to the spans.
    #     """
    #     text_blocks = page_content["text_data"][0]  # Extract text_blocks from page_content

    #     # Extract all unique fonts from spans
    #     font_list = []
    #     for block in text_blocks:
    #         for line in block.get("lines", []):
    #             for span in line.get("spans", []):
    #                 if "font" in span:
    #                     font_list.append(span["font"])
    #     font_list = list(set(font_list))  # Remove duplicates

    #     # Initialize a dictionary to hold clusters
    #     clusters = {}

    #     # Custom function to find the shortest word in a list
    #     def find_shortest_word(word_list):
    #         return min(word_list, key=len)

    #     # Custom function to find the root of a word using regex
    #     def find_root(word):
    #         match = re.match(r'([A-Za-z][A-Za-z]+)', word)
    #         return match.group(1) if match else word

    #     # Cluster fonts based on their root
    #     while font_list:
    #         shortest_word = find_shortest_word(font_list)
    #         root = find_root(shortest_word)
    #         for word in font_list.copy():  # Iterate over a copy to safely modify the original list
    #             if root in word:
    #                 clusters[word] = root
    #                 font_list.remove(word)

    #     # Update spans with the font clusters
    #     for block in text_blocks:
    #         for line in block.get("lines", []):
    #             for span in line.get("spans", []):
    #                 if "font" in span and span["font"] in clusters:
    #                     span["font_cluster"] = clusters[span["font"]]

    #     # Update page_content with the modified text blocks
    #     page_content["text_data"] = (text_blocks, page_content["text_data"][1])

    #     return page_content

    # def _normalize_font_sizes(self, page_content: dict) -> dict:
    #  """
    #     Normalizes font sizes across the extracted text blocks within the page_content dictionary.

    #     Args:
    #         page_content (dict): A dictionary containing page data, including 'text_data'.

    #     Returns:
    #         dict: The updated page_content dictionary with normalized font size information added
    #             to each text block under the key 'normalized_font_size'.
    #     """
    #   text_blocks = page_content["text_data"][0]  # Extract text_blocks from page_content

    #    # Ensure max_font_size and min_font_size are set as object variables
    #    if not hasattr(self, "_max_font_size") or not hasattr(self, "_min_font_size"):
    #         raise AttributeError(
    #             "Object variables '_max_font_size' and '_min_font_size' must be set before calling this method."
    #         )

    #     # Normalize font sizes and add them to the text blocks
    #     font_size_range = self._max_font_size - self._min_font_size
    #     for block in text_blocks:
    #         normalized_size = round(
    #             (block['font_size'] - self._min_font_size) /
    #             font_size_range, 2
    #         )
    #         block['normalized_font_size'] = normalized_size

    #     # Update the page_content dictionary with the modified text blocks
    #     page_content["text_data"] = (text_blocks, page_content["text_data"][1])

    #     return page_content

    # def _calculate_min_max_font_size(self) -> None:
    #     """
    #     Calculates the minimum and maximum font sizes across the entire document
    #     using the precomputed data stored in `self._document_content`.

    #     This method updates the following object variables:
    #         - self._max_font_size: The largest font size found in the document.
    #         - self._min_font_size: The smallest font size found in the document.

    #     Raises:
    #         AttributeError: If `self._document_content` is not initialized or if the
    #                         constants for allowed font sizes are not set.
    #     """
    #     if not hasattr(self, "_document_content") or not self._document_content:
    #         raise AttributeError(
    #             "The document content 'self._document_content' is not initialized or empty."
    #         )

    #     # Ensure constants for allowed font sizes are defined
    #     if not hasattr(self, "_min_allowed_font_size") or not hasattr(self, "_max_allowed_font_size"):
    #         raise AttributeError(
    #             "The object must have '_min_allowed_font_size' and '_max_allowed_font_size' constants defined."
    #         )

    #     # Initialize global min and max font sizes with object constants
    #     # Start with the maximum allowed value
    #     global_min_font_size = self._max_allowed_font_size
    #     # Start with the minimum allowed value
    #     global_max_font_size = self._min_allowed_font_size

    #     # Iterate through page-level max and min font sizes
    #     for page_content in self._document_content:
    #         page_max = page_content.get(
    #             "max_font_size", self._min_allowed_font_size)
    #         page_min = page_content.get(
    #             "min_font_size", self._max_allowed_font_size)

    #         # Update global max and min font sizes
    #         global_max_font_size = max(global_max_font_size, page_max)
    #         global_min_font_size = min(global_min_font_size, page_min)

    #     self._max_font_size = global_max_font_size
    #     self._min_font_size = global_min_font_size
