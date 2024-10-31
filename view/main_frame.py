import tkinter as tk
from tkinter import ttk
from view.interfaces import IMainFrame, ITextAnnotationView, IPDFExtractionView, ITextComparisonView

class MainFrame(tk.Frame, IMainFrame):
    def __init__(self, parent_frame: tk.Frame, 
                 pdf_view: IPDFExtractionView, 
                 text_annotation_view: ITextAnnotationView, 
                 text_comparison_view: ITextComparisonView) -> None:
        """
        Initializes the MainFrame with its dependencies for each notebook page
        and immediately renders the notebook with three tabs.

        Args:
            parent_frame (tk.Frame): The parent frame where this main frame will be placed.
            pdf_view (IPDFExtractionView): The view for PDF extraction.
            text_annotation_view (ITextAnnotationView): The view for text annotation.
            text_comparison_view (ITextComparisonView): The view for text comparison.
        """
        super().__init__(parent_frame)
        self._pdf_view = pdf_view
        self._text_annotation_view = text_annotation_view
        self._text_comparison_view = text_comparison_view
        self._render(parent_frame)  # Call _render to set up the UI structure
    
    def _render(self, parent_frame: tk.Frame) -> None:
        """
        Sets up the MainFrame layout by creating a notebook and adding 
        the PDF extraction, text annotation, and text comparison views as separate tabs.

        Args:
            parent_frame (tk.Frame): The parent frame where this main frame will be placed.
        """
        # Create a notebook widget within the main frame
        notebook = ttk.Notebook(parent_frame)
        notebook.pack(fill="both", expand=True)

        # Add the PDF Extraction tab
        pdf_frame = tk.Frame(notebook)
        self._pdf_view.render(pdf_frame)  # Render PDF extraction view into this frame
        notebook.add(pdf_frame, text="PDF Extraction")

        # Add the Text Annotation tab
        text_annotation_frame = tk.Frame(notebook)
        self._text_annotation_view.render(text_annotation_frame)  # Render text annotation view into this frame
        notebook.add(text_annotation_frame, text="Text Annotation")

        # Add the Text Comparison tab
        text_comparison_frame = tk.Frame(notebook)
        self._text_comparison_view.render(text_comparison_frame)  # Render text comparison view into this frame
        notebook.add(text_comparison_frame, text="Text Comparison")
