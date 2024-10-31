import tkinter as tk
from view.interfaces import IPDFExtractionView

class PDFExtractionView(IPDFExtractionView):
    def render(self, parent_frame):
        frame = tk.Frame(parent_frame)
        # Add PDF extraction widgets here
        frame.pack(fill="both", expand=True)
        return frame
