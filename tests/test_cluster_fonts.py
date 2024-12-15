from scripts.extraction_script import PDFExtractor


def test_cluster_fonts():
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
        assert cluster_name == expected_clusters[
            font_name], f"Font '{font_name}' not clustered correctly."

    print("Test passed: All fonts clustered correctly.")
