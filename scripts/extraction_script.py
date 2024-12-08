

from io import BytesIO
from PIL import Image
from pprint import pprint
from pymupdf import Rect
import pymupdf
from pathlib import Path


class PDFExtractor:
    def __init__(self, pdf_path: str, min_area: int = 1000, min_size: int = 10, max_line_spacing: int = 5, tolerance: int = 2, consider_bg_colors: bool = False):
        """
        Initializes the PDFExtractor with the given PDF path and margins.

        Args:
            pdf_path (str): Path to the PDF file.
            margins (list[int]): Margins for clipping (left, top, right, bottom).
            min_area (int): Minimum area for considering a bounding box.
            min_size (int): Minimum size for considering a bounding box.
        """
        self.pdf_path = Path(pdf_path)
        self.min_area = min_area
        self.min_size = min_size
        self.consider_bg_colors = consider_bg_colors
        self.max_line_spacing = max_line_spacing
        self.tolerance = tolerance
        self.doc = pymupdf.open(self.pdf_path)

    def get_page(self, page_number: int):
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
        left = margins[0]
        top = margins[1]
        right = page.rect.width - margins[2]
        bottom = page.rect.height - margins[3]
        clip_rect = Rect(left, top, right, bottom)

        # Get text blocks within clipped area
        text_blocks = page.get_text("dict", clip=clip_rect)["blocks"]

        # if no text found on this page
        if not text_blocks:
            return []

        # Filter non-horizontal text blocks
        non_horizontal_text_blocks = [
            block for block in text_blocks
            if block.get("lines") and len(block["lines"]) > 0 and block["lines"][0]["dir"] != (1.0, 0.0)
        ]

        non_horizontal_text_bboxes = [
            Rect(block["bbox"]).irect for block in non_horizontal_text_blocks
        ]

        text_blocks = [
            block for block in text_blocks if block not in non_horizontal_text_blocks
        ]

        # Find table, image, and graphic boxes
        tables = page.find_tables()
        table_bboxes = [Rect(table.bbox).irect for table in tables]

        images = page.get_images()
        image_bboxes = [page.get_image_rects(
            image)[0].irect for image in images]

        graphics = page.get_drawings()
        graphic_bboxes = [graphic["rect"].irect for graphic in graphics]

        background_bboxes = [
            box
            for box in graphic_bboxes
            if box.width * box.height > self.min_area and min(box.width, box.height) > self.min_size
        ]

        graphic_bboxes = [
            graphic_bbox for graphic_bbox in graphic_bboxes if graphic_bbox not in background_bboxes]

        obstacle_bboxes = non_horizontal_text_bboxes + \
            table_bboxes+image_bboxes+graphic_bboxes
        if self.consider_bg_colors:
            obstacle_bboxes += background_bboxes

        # Ignore tables
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

        #######################
        text_blocks, text_bboxes = self._sort_text_blocks(
            text_blocks, text_bboxes, background_bboxes)

        #######################

        # Extend text bounding boxes to the right edge of the page, stopping at obstacles
        for index, text_bbox in enumerate(text_bboxes):
            # Start by extending the box to the right edge of the page
            extended_bbox = Rect(text_bbox.x0, text_bbox.y0,
                                 right, text_bbox.y1).irect

            # Check for collisions with obstacles
            for obstacle_bbox in obstacle_bboxes:
                # Stop at the first obstacle
                if extended_bbox.intersects(obstacle_bbox):
                    # Adjust the right edge
                    extended_bbox.x1 = min(extended_bbox.x1, obstacle_bbox.x0)

            # Prevent merging across columns
            tolerance = 1  # Allow a 1-pixel tolerance to avoid rounding issues
            for other_bbox in text_bboxes:
                if other_bbox == text_bbox:  # Skip the current box
                    continue
                if other_bbox.x0 > text_bbox.x1 + tolerance:  # Check if other box is to the right with a positive gap
                    # Adjust the right edge
                    extended_bbox.x1 = min(extended_bbox.x1, other_bbox.x0)

            # Update the bounding box
            text_bboxes[index] = extended_bbox

        text_blocks, text_bboxes = self._sort_text_blocks(
            text_blocks, text_bboxes, background_bboxes)

        #######################
        # Merge close or overlapping text_blocks
        # Initialize merged lists with the first block and bounding box
        merged_text_blocks = [text_blocks[0]]
        merged_text_bboxes = [text_bboxes[0]]

        # Iterate over the remaining blocks and bounding boxes
        for block, text_bbox in zip(text_blocks[1:], text_bboxes[1:]):
            # Get the last merged bounding box
            last_text_bbox = merged_text_bboxes[-1]

            # Check if the rectangles intersect or are left-aligned with a small horizontal gap
            intersects = text_bbox.intersects(last_text_bbox)
            # Horizontal distance
            horizontal_gap = abs(text_bbox.y0 - last_text_bbox.y1)

            # Check alignment and gap
            left_alignment = abs(
                text_bbox.x0 - last_text_bbox.x0) <= self.tolerance
            within_max_spacing = horizontal_gap <= self.max_line_spacing

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

        # Update the final text_blocks and text_bboxes
        text_blocks = merged_text_blocks
        text_bboxes = merged_text_bboxes

        self.visualize_bboxes(page, text_bboxes, obstacle_bboxes)

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

    def _sort_text_blocks(self, text_blocks: list, text_bboxes: list, background_bboxes: list = None) -> tuple[list, list]:
        # Sorting and handling background colors
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
        return map(list, zip(*combined)) if combined else ([], [])

    #!just for debugging

    def visualize_bboxes(self, page, text_bboxes, obstacle_bboxes):
        """
            Visualizes bounding boxes on the given page by drawing red rectangles
            and writing the index of each box in its center.

            Args:
                page (Page): The PyMuPDF page object to annotate.
                text_bboxes (list[Rect]): List of bounding boxes to visualize.
            """
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
            # Draw the bounding box in red
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
DOCUMENT = 1
TEST_PAGE = 11
margins = [10, 10, 10, 10]
pdf_extractor = PDFExtractor(pdf_path=f"{test_pdf_path}/{test_docs[DOCUMENT]}")
page = pdf_extractor.get_page(TEST_PAGE)
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
