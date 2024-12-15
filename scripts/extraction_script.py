

from io import BytesIO
import re
from PIL import Image
from pprint import pprint
from pymupdf import Rect
import pymupdf
from pathlib import Path


class PDFExtractor:
    def __init__(self, pdf_path: str = "", consider_bg_colors: bool = False, ignore_tables: bool = True, ignore_headlines: bool = True):
        """
        Initializes the PDFExtractor with the given PDF path and various processing options.

        Args:
            pdf_path (str, optional): Path to the PDF file. Default is an empty string.
            consider_bg_colors (bool, optional): Whether to consider background colors during processing. Default is False.
            ignore_tables (bool, optional): Whether to ignore tables when extracting text. Default is True.
            ignore_headlines (bool, optional): Whether to ignore headlines when processing text. Default is True.
        """
        if pdf_path:
            self._switch_document(pdf_path)

        self.consider_bg_colors = consider_bg_colors
        self.ignore_tables = ignore_tables
        self.ignore_headlines = ignore_headlines

        # Minimum area for considering a bounding box as part of the background
        self._min_area_for_background = 1000

        # Minimum size (width or height) for considering a bounding box as part of the background
        self._min_size_for_background = 10

        # Maximum vertical spacing between lines within the same text block
        self._max_line_vertical_spacing = 5

        # Tolerance for considering two text blocks to be left-aligned
        self._left_alignment_tolerance = 2

        # Vertical overlap tolerance (in pixels) for obstacles when extending bounding boxes
        self._vertical_overlap_tolerance = 3

        # Column gap tolerance (in pixels) for preventing merging across columns
        self._column_gap_tolerance = 1

    def _switch_document(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = pymupdf.open(self.pdf_path)

    def _get_page(self, page_number: int):
        """
        Retrieves a page from the PDF.

        Args:
            page_number (int): Page number to retrieve.

        Returns:
            Page: The specified page object.
        """
        return self.doc[page_number]

    def find_connected_text_boxes(self, page, margins):
        """
        Finds connected text boxes on a page, considering margins and optional background colors.

        Args:
            page: The page object to analyze.
            consider_bg_colors (bool): Whether to consider background colors in the analysis.
        """
        page_content = self._extract_page_content(page, margins)
        page_content = self._sort_text_data(page_content)
        page_content = self._extend_bounding_boxes(page_content)
        page_content = self._sort_text_data(page_content)
        page_content = self._merge_text_boxes(page_content)
        self.visualize_bboxes(page, page_content)

    def _extract_page_content(self, page, page_margins):
        # geometric data
        left = page_margins[0]
        top = page_margins[1]
        right = page.rect.width - page_margins[2]
        bottom = page.rect.height - page_margins[3]
        clip_rect = Rect(left, top, right, bottom)

        # Get text blocks within clipped area
        text_blocks = page.get_text("dict", clip=clip_rect)["blocks"]

        # If no text found on this page
        if not text_blocks:
            return []

        # Separate horizontal and non-horizontal text blocks in one pass
        non_horizontal_text_bboxes = []
        filtered_text_blocks = []

        for block in text_blocks:
            if block.get("lines") and len(block["lines"]) > 0 and block["lines"][0]["dir"] != (1.0, 0.0):
                non_horizontal_text_bboxes.append(Rect(block["bbox"]).irect)
            else:
                filtered_text_blocks.append(block)

        # Update text_blocks to only contain horizontal text blocks
        text_blocks = filtered_text_blocks

        # Find table, image, and graphic boxes
        tables = page.find_tables()
        table_bboxes = [Rect(table.bbox).irect for table in tables]

        images = page.get_images()
        image_bboxes = [page.get_image_rects(
            image)[0].irect for image in images]

        graphics = page.get_drawings()
        graphic_bboxes = [graphic["rect"].irect for graphic in graphics]

        background_bboxes = []
        filtered_graphic_bboxes = []

        for box in graphic_bboxes:
            if box.width * box.height > self._min_area_for_background and min(box.width, box.height) > self._min_size_for_background:
                background_bboxes.append(box)
            else:
                filtered_graphic_bboxes.append(box)

        graphic_bboxes = filtered_graphic_bboxes

        obstacle_bboxes = non_horizontal_text_bboxes + \
            table_bboxes+image_bboxes+graphic_bboxes
        if self.consider_bg_colors:
            obstacle_bboxes += background_bboxes

        # Ignore tables
        if self.ignore_tables:
            text_blocks = [block for block in text_blocks if not any(
                self._is_bbox_within(Rect(block["bbox"]).irect, table_bbox) for table_bbox in table_bboxes)]

        # Combine lines within blocks into bounding boxes
        text_bboxes = []
        for block in text_blocks:
            # Skip blocks without "lines" or empty "lines" lists
            if not block.get("lines") or len(block["lines"]) == 0:
                continue

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

        return {
            "geometry": clip_rect,
            "text_data": (text_blocks, text_bboxes),
            "obstacles": obstacle_bboxes,
            "backgrounds": background_bboxes
        }

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
        page_content["text_data"] = map(
            list, zip(*combined)) if combined else ([], [])

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

    def _cluster_fonts(self, text_blocks):
        """
        Clusters fonts found in text blocks and updates the blocks to reflect font families.

        This method lists all occurring fonts, creates a dictionary mapping individual fonts
        to their stems, and updates the text blocks to use these stems, aiding in identification
        of headings by normalizing font variations.

        Parameters:
        text_blocks (list[dict]): The text blocks extracted from the PDF document.

        Returns:
        list[dict]: The updated list of text blocks with fonts mapped to their stems.
        """
        # Extract all occurring fonts from the text blocks
        font_list = [block['font_name'] for block in text_blocks]
        font_list = list(set(font_list))  # Remove duplicates

        # Initialize a dictionary to hold clusters
        clusters = {}

        # Custom function to find the shortest word in a list
        def find_shortest_word(word_list):
            return min(word_list, key=len)

        # Custom function to find the root of a word using regex
        def find_root(word):
            match = re.match(r'([A-Za-z][a-z]+)', word)
            return match.group(1) if match else word

        # Cluster words based on their root
        while font_list:
            shortest_word = find_shortest_word(font_list)
            root = find_root(shortest_word)
            for word in font_list.copy():  # Iterate over a copy to safely modify the original list
                if root in word:
                    clusters[word] = root
                    font_list.remove(word)

        # Update text blocks with the font stems
        for block in text_blocks:
            if block['font_name'] in clusters:
                block['font_name_cluster'] = clusters[block['font_name']]

        return text_blocks

    def _normalize_font_sizes(self, text_blocks):
        # todo change out
        """
        Normalizes font sizes across the extracted text blocks.

        Parameters:
        text_blocks (list[dict]): List of dictionaries containing text block properties.

        Returns:
        list[dict]: The list with normalized font size information.
        """
        # Find the maximum and minimum font sizes in the document
        max_font_size = max(block['font_size'] for block in text_blocks)
        min_font_size = min(block['font_size'] for block in text_blocks)
        # Normalize font sizes to a range, e.g., 0-1
        for block in text_blocks:
            normalized_size = round((
                block['font_size'] - min_font_size) / (max_font_size - min_font_size), 2)
            block['normalized_font_size'] = normalized_size

        return text_blocks

    #!just for debugging

    def visualize_bboxes(self, page, page_content: dict) -> None:
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

        # Show the image using Pillow
        img.show()


# Example usage:
test_pdf_path = "test_data/pdf"
test_docs = [
    "Grundwasser-Überwachungsprogramm - 2022.pdf",
    "Auf zu neuen Wegen – gemeinschaftlich und nachhaltig wirtschaften!_2022.pdf",
]
DOCUMENT = 0
TEST_PAGE = 31
margins = [10, 10, 10, 10]
pdf_extractor = PDFExtractor(pdf_path=f"{test_pdf_path}/{test_docs[DOCUMENT]}")
page = pdf_extractor._get_page(TEST_PAGE)
pdf_extractor.find_connected_text_boxes(page, margins)


# tabs = page.find_tables()
# print(f"{len(tabs.tables)} table(s) on {page}")

# text = ""
# if tabs:
#     top = margins[1]
#     bottom = page.rect.height - margins[3]
#     for tab in tabs:
#         print(f"{tab.header.names=}")
#         tab_top = tab.bbox[1]
#         tab_bottom = tab.bbox[3]
#         # if there is relevant space above the table
#         print(f"{(top,tab_top)=}")
#         if top < tab_top:
#             clip_rect = Rect(
#                 left,
#                 top,
#                 right,
#                 tab_top
#             )
#             print(f"{clip_rect=}")
#             text += page.get_text(clip=clip_rect)
#         top = tab_bottom
#         if top >= bottom:
#             break
# else:
#     clip_rect = Rect(
#         left,
#         top,
#         right,
#         bottom
#     )
#     text += page.get_text(clip=clip_rect)
# print(text)
