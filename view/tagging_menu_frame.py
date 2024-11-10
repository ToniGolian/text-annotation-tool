import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from controller.interfaces import IController
from view.tag_frame import TagFrame


class TaggingMenuFrame(tk.Frame):
    """
    A tkinter Frame that contains a Notebook with pages representing template groups.
    """

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the TaggingMenuFrame with a Notebook containing pages for each template group.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TaggingMenuFrame.
            controller (IController): The controller that provides template groups.
        """
        super().__init__(parent)

        # Store controller and retrieve template groups
        self._controller = controller
        self._template_groups: List[Dict] = self._controller.get_template_groups(
        )

        # Create the internal notebook
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        # Render the initial pages in the notebook
        self._render()

    def _render(self) -> None:
        """
        Renders pages in the notebook for each template group.
        """
        # Add a page for each template group
        for group in self._template_groups:
            group_name = group.get("group_name")
            templates = group.get("templates")
            page_frame = self._render_single_page(templates)
            self._notebook.add(page_frame, text=group_name)

    def _render_single_page(self, templates: List[Dict]) -> tk.Frame:
        """
        Renders a scrollable page with TagFrames based on the provided templates.

        Args:
            templates (List[Dict]): A list of templates to be displayed in the page.

        Returns:
            tk.Frame: A scrollable frame with TagFrames for each template.
        """
        # Create a container frame to contain the canvas and scrollbar
        container_frame = tk.Frame(self)

        # Create the canvas and scrollbar
        canvas = tk.Canvas(container_frame)
        scrollbar = ttk.Scrollbar(
            container_frame, orient="vertical", command=canvas.yview)

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas that will be scrollable
        scrollable_frame = tk.Frame(canvas)

        # Update the scrollable frame width to match the canvas width
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Force the canvas width to match the container_frame's width
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                "scrollable_window", width=canvas.winfo_width())
        )

        # Add the scrollable frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame,
                             anchor="nw", tags="scrollable_window")

        # Add TagFrames for each template in the group
        j = 0
        for _ in range(3):
            for template in templates:
                tag_frame = TagFrame(scrollable_frame, template)
                if j % 2 == 0:
                    tag_frame.config(bg="red")
                else:
                    tag_frame.config(bg="green")
                j += 1
                tag_frame.pack(fill="x", padx=5, pady=5,
                               anchor="n", expand=True)

        # Pack the canvas and scrollbar inside the container frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container_frame
