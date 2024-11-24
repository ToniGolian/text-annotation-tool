import tkinter as tk
from tkinter import ttk
from typing import Dict


class AnnotationTagFrame(tk.Frame):
    """
    A tkinter Frame that dynamically generates form fields based on a given template.

    Attributes:
        template (Dict): The template dictionary defining the structure and attributes for the tag.
    """

    def __init__(self, parent: tk.Widget, template: Dict) -> None:
        """
        Initializes the TagFrame and creates widgets based on the template.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TagFrame.
            template (Dict): The template dictionary defining the tag type and attributes.
        """
        super().__init__(parent)
        self.template = template
        self._render()

    def _render(self) -> None:
        """
        Renders widgets for the tag based on the template, adding labels and entry or combobox widgets for each active attribute.
        """
        # Configure grid columns: column 0 to fit contents, column 1 to expand
        self.grid_columnconfigure(0, weight=0)  # Left column for labels
        # Right column for entry widgets
        self.grid_columnconfigure(1, weight=1)

        # Display header label
        tag_type = self.template.get("type", "Tag")
        header_label = tk.Label(
            self, text=f"{tag_type} Tag", font=("Helvetica", 16))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Iterate over each attribute in the template
        row = 1  # Start placing widgets from row 1
        for attr_name, attr_data in self.template.get("attributes", {}).items():
            # Check if the attribute is active
            if not attr_data.get("active", False):
                continue

            # Create label for the attribute
            label = tk.Label(self, text=attr_name)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)

            # Choose widget based on the type
            if attr_data.get("type") == "CDATA":
                # Entry widget for CDATA type
                widget = tk.Entry(self)
                default_value = attr_data.get("default")
                if default_value:
                    widget.insert(0, default_value)

            else:
                # Combobox for other types
                allowed_values = attr_data.get("allowedValues", [])
                widget = ttk.Combobox(self, values=allowed_values)
                default_value = attr_data.get("default")
                if default_value and default_value in allowed_values:
                    widget.set(default_value)

            # Place the widget in the grid, making it expand in the horizontal direction
            widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            row += 1
