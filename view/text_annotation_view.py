import tkinter as tk
from tkinter import ttk
from view.interfaces import ITextAnnotationView, IPDFExtractionView, ITextDisplayView, ITextComparisonView

class TextAnnotationView(ITextAnnotationView):
    def __init__(self, parent_frame: tk.Frame, 
                 pdf_view: IPDFExtractionView, 
                 text_display_view: ITextDisplayView, 
                 text_comparison_view: ITextComparisonView) -> None:
        """
        Initializes the TextAnnotationView with its dependencies for each notebook page
        and renders the notebook immediately.
        
        Args:
            parent_frame (tk.Frame): The parent frame where this view will be placed.
            pdf_view (IPDFExtractionView): The view for PDF extraction.
            text_display_view (ITextDisplayView): The view for text annotation.
            text_comparison_view (ITextComparisonView): The view for text comparison.
        """
        super().__init__(parent_frame)
        self._pdf_view = pdf_view
        self._text_display_view = text_display_view
        self._text_comparison_view = text_comparison_view
        self._render(parent_frame)  # Call _render to set up the UI
    
    def _render(self, parent_frame: tk.Frame) -> None:
        """
        Renders the TextAnnotationView, organizing the PDF extraction, text annotation, 
        and text comparison views in a notebook.

        Args:
            parent_frame (tk.Frame): The parent frame where this view will be placed.
        """
        notebook = ttk.Notebook(parent_frame)
        notebook.pack(fill="both", expand=True)

        # Add the PDF Extraction tab
        pdf_frame = tk.Frame(notebook)
        self._pdf_view.render(pdf_frame)
        notebook.add(pdf_frame, text="PDF Extraction")

        # Add the Text Annotation tab
        text_annotation_frame = tk.Frame(notebook)
        self._text_display_view.render(text_annotation_frame)
        notebook.add(text_annotation_frame, text="Text Annotation")

        # Add the Text Comparison tab
        text_comparison_frame = tk.Frame(notebook)
        self._text_comparison_view.render(text_comparison_frame)
        notebook.add(text_comparison_frame, text="Text Comparison")
