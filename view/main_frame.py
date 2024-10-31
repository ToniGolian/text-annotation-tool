import tkinter as tk
from tkinter import ttk
from view.pdf_extraction_view import PDFExtractionView
from view.text_annotation_view import  TextAnnotationView
from view.text_comparison_view import TextComparisonView  
from controller.interfaces import IController

class MainFrame(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the MainFrame and immediately renders the notebook with three tabs.

        Args:
            parent (tk.Widget): The parent widget where this main frame will be placed.
        """
        super().__init__(parent)
        self.controller=controller
        self._render()  # Call _render to set up the UI structure
    
    def _render(self) -> None:
        """
        Sets up the MainFrame layout by creating a notebook and adding 
        the PDF extraction, text annotation, and text comparison views as separate tabs.
        """
        # Create a notebook widget within the main frame
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Add the PDF Extraction tab
        pdf_frame = tk.Frame(notebook)
        pdf_view = PDFExtractionView(parent=self,controller=self.controller)  # Directly instantiate PDF extraction view
        pdf_view._render()  
        notebook.add(pdf_frame, text="PDF Extraction")

        # Add the Text Annotation tab
        text_annotation_frame = tk.Frame(notebook)
        text_annotation_view = TextAnnotationView(parent=self,controller=self.controller)  # Direct instantiation
        text_annotation_view._render()
        notebook.add(text_annotation_frame, text="Text Annotation")

        # Add the Text Comparison tab
        text_comparison_frame = tk.Frame(notebook)
        text_comparison_view = TextComparisonView(parent=self,controller=self.controller)  # Direct instantiation
        text_comparison_view._render()
        notebook.add(text_comparison_frame, text="Text Comparison")
