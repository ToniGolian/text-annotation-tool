import tkinter as tk
from tkinter import ttk
from typing import Dict

class TaggingMenuFrame(ttk.Notebook):
    """
    A tkinter Notebook that contains pages with scrollable frames, where each page represents a template group.
    
    Attributes:
        _controller: The controller reference used to access template groups.
        _template_groups: The dictionary of template groups retrieved from the controller.
    """

    def __init__(self, parent: tk.Widget, controller) -> None:
        """
        Initializes the TaggingMenuFrame with pages representing template groups.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TaggingMenuFrame.
            controller: The controller that provides template groups.
        """
        super().__init__(parent)
        self._controller = controller
        self._template_groups = self._controller.get_template_groups()
        self._render_pages()

    def _render_pages(self) -> None:
        """
        Renders pages in the notebook for each template group, with each page containing scrollable TagFrames.
        """
        # Clear any existing pages
        for child in self.winfo_children():
            child.destroy()

        # Render new pages based on updated template groups
        for group_name, templates in self._template_groups.items():
            page_frame = self._render_scrollable_frame(self)
            self.add(page_frame, text=group_name)

            for template in templates:
                tag_frame = TagFrame(page_frame, template)
                tag_frame.pack(fill='x', padx=10, pady=5, anchor='n')

    def _render_scrollable_frame(self, container: tk.Widget) -> tk.Frame:
        """
        Renders a scrollable frame with a vertical scrollbar on the right side.

        Args:
            container (tk.Widget): The container widget for the scrollable frame.

        Returns:
            tk.Frame: A frame with a vertical scrollbar.
        """
        frame = tk.Frame(container)
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        frame.pack(fill="both", expand=True)

        return scrollable_frame

    def update_template_groups(self) -> None:
        """
        Updates the template groups from the controller and re-renders the pages in the notebook.
        """
        self._template_groups = self._controller.get_template_groups()
        self._render_pages()
