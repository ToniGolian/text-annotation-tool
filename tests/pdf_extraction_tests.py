import unittest
from unittest.mock import MagicMock, Mock
from utils.pdf_extractor import PDFExtractor


class TestClusterFonts(unittest.TestCase):
    def test_cluster_fonts(self):
        # Mock page_content with text_blocks containing font names
        page_content = {
            "text_data": (
                [
                    {"font_name": "Arial-Bold", "text": "Heading 1"},
                    {"font_name": "Arial-Italic", "text": "Heading 2"},
                    {"font_name": "TimesNewRoman-Regular", "text": "Body text"},
                    {"font_name": "TimesNewRoman-Bold", "text": "Body text bold"},
                    {"font_name": "Courier-New", "text": "Code block"},
                ],
                []  # Mock text_bboxes (not relevant for this test)
            ),
            "obstacles": [],
            "backgrounds": [],
            "geometry": None,
        }

        # Expected font clusters
        expected_clusters = {
            "Arial-Bold": "Arial",
            "Arial-Italic": "Arial",
            "TimesNewRoman-Regular": "TimesNewRoman",
            "TimesNewRoman-Bold": "TimesNewRoman",
            "Courier-New": "Courier",
        }

        # Instantiate the class
        extractor = PDFExtractor()

        # Run the method
        updated_page_content = extractor._cluster_fonts(page_content)

        # Extract updated text_blocks
        updated_text_blocks = updated_page_content["text_data"][0]

        # Assert each block's clustered font name
        for block in updated_text_blocks:
            font_name = block["font_name"]
            cluster_name = block.get("font_name_cluster")
            self.assertEqual(
                cluster_name, expected_clusters[font_name],
                f"Font '{font_name}' not clustered correctly."
            )


class TestCalculateMinMaxFontSize(unittest.TestCase):
    def setUp(self):
        # Create a PDFExtractor instance
        self.extractor = PDFExtractor()

        # Mock the doc object using MagicMock for iteration
        self.extractor.doc = MagicMock()

    def test_calculate_min_max_font_size(self):
        # Mock page objects with font sizes
        self.extractor.doc.__iter__.return_value = iter([
            MagicMock(get_text=MagicMock(return_value={
                "blocks": [
                    {"lines": [{"spans": [{"size": 12}, {"size": 10}]}]},
                    {"lines": [{"spans": [{"size": 14}, {"size": 8}]}]},
                ]
            })),
            MagicMock(get_text=MagicMock(return_value={
                "blocks": [
                    {"lines": [{"spans": [{"size": 16}, {"size": 6}]}]},
                ]
            })),
        ])

        # Run the method
        self.extractor._calculate_min_max_font_size()

        # Assert max and min font sizes
        self.assertEqual(self.extractor._max_font_size,
                         16, "Max font size should be 16.")
        self.assertEqual(self.extractor._min_font_size,
                         6, "Min font size should be 6.")

    def test_empty_document(self):
        # Mock an empty document
        self.extractor.doc.__iter__.return_value = iter([])

        # Run the method
        self.extractor._calculate_min_max_font_size()

        # Assert max and min font sizes are 0 for an empty document
        self.assertEqual(self.extractor._max_font_size, 0,
                         "Max font size should be 0 for an empty document.")
        self.assertEqual(self.extractor._min_font_size, 0,
                         "Min font size should be 0 for an empty document.")

    def test_missing_lines_or_spans(self):
        # Mock a document with no valid font size data
        self.extractor.doc.__iter__.return_value = iter([
            MagicMock(get_text=MagicMock(
                return_value={"blocks": [{"lines": []}]})),
            MagicMock(get_text=MagicMock(return_value={"blocks": []})),
        ])

        # Run the method
        self.extractor._calculate_min_max_font_size()

        # Assert max and min font sizes are 0 for missing data
        self.assertEqual(self.extractor._max_font_size, 0,
                         "Max font size should be 0 for missing lines or spans.")
        self.assertEqual(self.extractor._min_font_size, 0,
                         "Min font size should be 0 for missing lines or spans.")


if __name__ == "__main__":
    unittest.main()
