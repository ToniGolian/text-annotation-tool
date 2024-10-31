import tkinter as tk
from view.interfaces import ITextComparisonView

class TextComparisonView(ITextComparisonView):
    def render(self, parent_frame):
        frame = tk.Frame(parent_frame)
        # Add Text comparison widgets here
        frame.pack(fill="both", expand=True)
        return frame
