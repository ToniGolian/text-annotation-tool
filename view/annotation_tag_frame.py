import tkinter as tk
from tkinter import ttk
from typing import Dict
from controller.interfaces import IController


class AnnotationTagFrame(tk.Frame):
    """
    A tkinter Frame that dynamically generates form fields based on a given template.

    Attributes:
        template (Dict): The template dictionary defining the structure and attributes for the tag.
    """

    def __init__(self, parent: tk.Widget, controller: IController, template: Dict) -> None:
        """
        Initializes the TagFrame and creates widgets based on the template.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TagFrame.
            controller (IController): The controller managing interactions.
            template (Dict): The template dictionary defining the tag type and attributes.
        """
        super().__init__(parent)
        self._controller = controller
        self._template = template
        self._data_widgets = {}
        self._selected_text_entry = None  # Entry for selected text
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
        tag_type = self._template.get("type", "Tag")
        header_label = tk.Label(
            self, text=f"{tag_type[0].upper()+tag_type[1:]}-Tag", font=("Helvetica", 16))
        header_label.grid(row=0, column=0, columnspan=2,
                          padx=10, pady=(0, 10), sticky="w")

        # Add "Selected Text" label and entry at the top
        selected_text_label = tk.Label(self, text="Selected Text")
        selected_text_label.grid(
            row=1, column=0, sticky="w", padx=(15, 5), pady=5)

        self._selected_text_entry = tk.Entry(self, state="disabled")
        self._selected_text_entry.grid(
            row=1, column=1, sticky="ew", padx=5, pady=5)
        # Iterate over each attribute in the template
        row = 2  # Start placing widgets from row 2
        for attr_name, attr_data in self._template["attributes"].items():
            # Create label for the attribute
            label = tk.Label(self, text=attr_name)
            label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)

            # Choose widget based on the type
            if attr_data["type"].upper() in ["CDATA", "ID"]:
                # Entry widget for CDATA type
                widget = tk.Entry(self)
            else:
                # Combobox for other types
                allowed_values = [""]
                if "allowedValues" in attr_data:
                    allowed_values = [""] + attr_data["allowedValues"]
                widget = ttk.Combobox(self, values=allowed_values)
                widget.set(allowed_values[0])

                if "default" in attr_data:
                    default_value = attr_data["default"]
                    if default_value and default_value in allowed_values:
                        widget.set(default_value)

            # Place the widget in the grid
            widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            # Store reference to the widget
            self._data_widgets[attr_name] = widget
            row += 1

        # Add "Add Tag" button
        add_tag_button = ttk.Button(
            self, text="Add Tag", command=self._button_pressed_add_tag)
        add_tag_button.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Add label and combobox for "ID to Edit"
        edit_label = tk.Label(self, text="ID to Edit")
        edit_label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)

        self.edit_id_combobox = ttk.Combobox(self, values=[""])
        self.edit_id_combobox.grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Add "Edit Tag" button
        edit_tag_button = ttk.Button(
            self, text="Edit Tag", command=self._button_pressed_edit_tag)
        edit_tag_button.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Add label and combobox for "ID to Delete"
        delete_label = tk.Label(self, text="ID to Delete")
        delete_label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)

        self.delete_id_combobox = ttk.Combobox(self, values=[""])
        self.delete_id_combobox.grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Add "Delete Tag" button
        delete_tag_button = ttk.Button(
            self, text="Delete Tag", command=self._button_pressed_delete_tag)
        delete_tag_button.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

    def set_selected_text(self, text: str) -> None:
        """
        Updates the "Selected Text" entry with the given text.

        Args:
            text (str): The selected text to display.
        """
        self._selected_text_entry.config(state="normal")
        self._selected_text_entry.delete(0, tk.END)
        self._selected_text_entry.insert(0, text)
        self._selected_text_entry.config(state="disabled")

    def _button_pressed_add_tag(self) -> None:
        """
        Handles the action when the 'Add Tag' button is pressed.
        """
        tag_data = self._collect_tag_data()
        self._controller.perform_add_tag(tag_data)

    def _button_pressed_edit_tag(self) -> None:
        """
        Handles the action when the 'Edit Tag' button is pressed.
        """
        tag_data = self._collect_tag_data()
        self._controller.perform_edit_tag(
            id=self.edit_id_combobox.get(), tag_data=tag_data)

    def _button_pressed_delete_tag(self) -> None:
        """
        Handles the action when the 'Delete Tag' button is pressed.
        """
        self._controller.perform_delete_tag(id=self.delete_id_combobox.get())

    def _collect_tag_data(self) -> dict:
        """
        Collects data from the widgets in self._data_widgets and returns it as a dictionary.
        Only includes non-empty values.

        Returns:
            dict: A dictionary containing the collected data.
        """
        return {
            attr_name: widget.get().strip()
            for attr_name, widget in self._data_widgets.items()
            if widget.get().strip()
        }
