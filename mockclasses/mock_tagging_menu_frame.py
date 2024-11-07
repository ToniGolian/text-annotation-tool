import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController


class MockTaggingMenuFrame(tk.Frame):
    """
    A mock tkinter Frame that contains a Notebook with two pages:
    one with five alternating colored frames, and one empty.
    """

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the MockTaggingMenuFrame with a Notebook containing two pages.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this MockTaggingMenuFrame.
            controller (IController): The controller interface for accessing data.
        """
        super().__init__(parent)

        # Create the internal notebook
        self._controller = controller
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        # Render the scrollable pages in the notebook
        self._render_pages()

    def _render_pages(self) -> None:
        """
        Renders two pages in the notebook: one with alternating colored frames and one empty green page.
        """
        # Add the yellow page with alternating colored frames
        yellow_page = self._render_scrollable_page_with_frames("yellow")
        self._notebook.add(yellow_page, text="Yellow Page")

        # Add an empty green page
        green_page = self._render_scrollable_page("green")
        self._notebook.add(green_page, text="Green Page")

    def _render_scrollable_page_with_frames(self, color: str) -> tk.Frame:
        """
        Renders a scrollable page with five alternating orange and green frames.

        Args:
            color (str): Background color for the page.

        Returns:
            tk.Frame: A scrollable frame with alternating colored frames.
        """
        # Create a container frame to contain the canvas and scrollbar
        container_frame = tk.Frame(self)

        # Create the canvas and scrollbar
        canvas = tk.Canvas(container_frame, bg=color)
        scrollbar = ttk.Scrollbar(
            container_frame, orient="vertical", command=canvas.yview)

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas that will be scrollable
        scrollable_frame = tk.Frame(canvas, bg=color)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Add the scrollable frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Add five alternating colored square frames
        colors = ["orange", "green"]
        for i in range(5):
            frame_color = colors[i % 2]  # Alternate between orange and green
            square_frame = tk.Frame(
                scrollable_frame, bg=frame_color, width=200, height=200)
            square_frame.pack(fill="both", expand=True)

        # Pack the canvas and scrollbar inside the container frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container_frame

    def _render_scrollable_page(self, color: str) -> tk.Frame:
        """
        Renders a scrollable page with a specified background color.

        Args:
            color (str): Background color for the page.

        Returns:
            tk.Frame: A scrollable frame with the specified background color.
        """
        # Create a container frame to contain the canvas and scrollbar
        container_frame = tk.Frame(self)

        # Create the canvas and scrollbar
        canvas = tk.Canvas(container_frame, bg=color)
        scrollbar = ttk.Scrollbar(
            container_frame, orient="vertical", command=canvas.yview)

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas that will be scrollable
        scrollable_frame = tk.Frame(canvas, bg=color)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Add the scrollable frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Pack the canvas and scrollbar inside the container frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container_frame
