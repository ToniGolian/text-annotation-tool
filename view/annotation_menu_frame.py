import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.annotation_tag_frame import AnnotationTagFrame
from view.interfaces import IAnnotationMenuFrame


class AnnotationMenuFrame(tk.Frame, IAnnotationMenuFrame):
    """
    A tkinter Frame that contains a Notebook with pages representing template groups.
    """

    def __init__(self, parent: tk.Widget, controller: IController, root_view_id: str) -> None:
        """
        Initializes the AnnotationMenuFrame with a Notebook containing pages for each template group.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TaggingMenuFrame.
            controller (IController): The controller that provides template groups.
        """
        super().__init__(parent)

        # Store controller and retrieve template groups
        self._controller = controller
        self._template_groups: List[Dict] = []

        # Create the internal notebook
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        self._controller.add_observer(self)

        self._tag_frames = []
        self._root_view_id = root_view_id

    def _render(self) -> None:
        """
        Renders pages in the notebook for each template group.
        """
        # Add a page for each template group
        for group in self._template_groups:
            group_name = group["group_name"]
            group_name = group_name[0].upper()+group_name[1:]
            group_templates = group["templates"]
            page_frame = self._render_single_page(group_templates)
            self._notebook.add(page_frame, text=group_name)

    def _render_single_page(self, group_templates: List[Dict]) -> tk.Frame:
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
        for template in group_templates:
            tag_frame = AnnotationTagFrame(
                parent=scrollable_frame, controller=self._controller, template=template, root_view_id=self._root_view_id)

            tag_frame.pack(fill="x", padx=5, pady=5,
                           anchor="n", expand=True)
            self._tag_frames.append(tag_frame)

        # Pack the canvas and scrollbar inside the container frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container_frame

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the observer based on the state changes from the given publisher.

        This method retrieves the updated state from the controller and processes both 
        data-related and layout-related changes in a unified way.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        state = self._controller.get_observer_state(self, publisher)
        print(f"DEBUG {state.keys()=}")
        # Handle selected text updates if available
        if "selected_text" in state:
            for tag_frame in self._tag_frames:
                tag_frame.set_selected_text(state["selected_text"])

        if "suggestions" in state:
            for tag_frame in self._tag_frames:
                suggestions = state["suggestions"][tag_frame.get_name()]
                tag_frame.set_attributes(suggestions)

        if "tags" in state:
            idref_list = [tag.get_id() for tag in state["tags"]]
            for tag_frame in self._tag_frames:
                tag_frame.set_idref_list(idref_list)

        # Handle layout updates if available
        if "template_groups" in state:
            self._template_groups = state["template_groups"]
            self._render()

    def finalize_view(self) -> None:
        """
        Retrieves the layout state and updates the filenames before rendering the view.
        """
        state = self._controller.get_observer_state(self)
        self._template_groups = state["template_groups"]
        self._render()
