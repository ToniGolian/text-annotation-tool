import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from controller.interfaces import IController


class AnnotationTagFrame(tk.Frame):
    """
    A tkinter Frame that dynamically generates form fields based on a given template.

    Attributes:
        template (Dict): The template dictionary defining the structure and attributes for the tag.
    """

    def __init__(self, parent: tk.Widget, controller: IController, template: Dict, root_view_id: str) -> None:
        """
        Initializes the TagFrame and creates widgets based on the template.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TagFrame.
            controller (IController): The controller managing interactions and commands for this frame.
            template (Dict): A dictionary defining the tag type and its associated attributes.
            root_view_id (str): The unique identifier of the root view (e.g., the notebook page) 
                                associated with this TagFrame, representing the top-level context 
                                for the specific task or subtask in the application.
        """
        super().__init__(parent)
        self._root_view_id = root_view_id
        self._controller = controller
        self._template = template
        self._data_widgets = {}
        self._idref_widgets = []  # list of widgets to chose references to other tags
        self._selected_text_entry = None  # Entry for selected text
        self._id_string = ""  # attributename f the id
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
        self.name = self._template.get("type", "Tag")
        header_label = tk.Label(
            self, text=f"{self.name[0].upper()+self.name[1:]}-Tag", font=("Helvetica", 16))
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
        for attribute_name, attribute_data in self._template["attributes"].items():
            # Create label for the attribute
            label = tk.Label(self, text=attribute_name)
            label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)

            attribute_type = attribute_data["type"].upper()
            # Choose widget based on the type
            if attribute_type.upper() in ["CDATA", "ID", "UNION"]:
                # Entry widget for CDATA type
                widget = tk.Entry(self)
            else:
                # Combobox for other types
                allowed_values = [""]
                if "allowedValues" in attribute_data:
                    allowed_values = [""] + attribute_data["allowedValues"]
                widget = ttk.Combobox(self, values=allowed_values)
                widget.set(allowed_values[0])

                if "default" in attribute_data:
                    default_value = attribute_data["default"]
                    if default_value and default_value in allowed_values:
                        widget.set(default_value)

            # Place the widget in the grid
            widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            # Rename attribute, if id
            if attribute_type == "ID":
                self._id_string = attribute_name
                attribute_name = "id"
            # Store reference to the widget
            self._data_widgets[attribute_name] = widget
            if attribute_type.upper() == "IDREF":
                self._idref_widgets.append(widget)
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
        self._idref_widgets.append(self.edit_id_combobox)
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
        self._idref_widgets.append(self.delete_id_combobox)
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
        if len(text) > 50:
            text = text[:50]+"..."
        self._selected_text_entry.config(state="normal")
        self._selected_text_entry.delete(0, tk.END)
        self._selected_text_entry.insert(0, text)
        self._selected_text_entry.config(state="disabled")

    def _button_pressed_add_tag(self) -> None:
        """
        Handles the action when the 'Add Tag' button is pressed.
        """
        tag_data = self._collect_tag_data()
        self._controller.perform_add_tag(
            tag_data=tag_data, caller_id=self._root_view_id)

    def _button_pressed_edit_tag(self) -> None:
        """
        Handles the action when the 'Edit Tag' button is pressed.
        """
        tag_data = self._collect_tag_data()
        self._controller.perform_edit_tag(
            tag_id=self.edit_id_combobox.get(), tag_data=tag_data, caller_id=self._root_view_id)

    def _button_pressed_delete_tag(self) -> None:
        """
        Handles the action when the 'Delete Tag' button is pressed.
        """
        self._controller.perform_delete_tag(
            tag_id=self.delete_id_combobox.get(), caller_id=self._root_view_id)

    def _collect_tag_data(self) -> dict:
        """
        Collects data from the widgets in self._data_widgets and returns it as a dictionary.

        The resulting dictionary includes:
            - "tag_type": The type of the tag as specified in the template.
            - "attributes": A list of tuples, where each tuple represents an attribute name-value pair.
            - "position": The position of the selected text in the document, retrieved from the controller.
            - "text": The currently selected text in the document.

        Returns:
            dict: A dictionary containing the collected tag data, including tag attributes, tag type,
                position, and the selected text.

        Raises:
            ValueError: If no text is currently selected.
        """
        # Retrieve the selected text and its position
        selected_text_data = self._controller.get_selected_text_data()
        selected_text = selected_text_data["selected_text"]
        position = selected_text_data["position"]

        if not selected_text:
            raise ValueError("No text is currently selected.")

        # Collect tag attributes from widgets
        attributes = {
            attribute_name: widget.get().strip()
            for attribute_name, widget in self._data_widgets.items()
            if widget.get().strip()
        }

        # # Change the attribute name for the id back to the tag specific id name
        # if "id" in attributes:
        #     attributes[self._id_string] = attributes.pop("id")

        # Build the tag data dictionary
        tag_data = {
            "tag_type": self._template.get("type", "Tag"),
            "attributes": attributes,
            "position": position,
            "text": selected_text,
            "id_string": self._id_string
        }

        return tag_data

    def get_name(self) -> str:
        """
        Retrieves the name of the menu frame.


        Returns:
            str: The name of the  menu frame.
        """
        return self.name

    def set_attributes(self, attribute_data: Dict[str, str]) -> None:
        """
        Populates the form fields with the given attribute data.

        This method updates the entry widgets corresponding to tag attributes
        with the provided values. It ensures that each attribute is displayed
        correctly in the UI.

        Args:
            attribute_data (Dict[str, str]): A dictionary where keys are attribute names 
                                             and values are their corresponding values to be set.
        """
        for widget in self._data_widgets.values():
            widget.delete(0, tk.END)

        for attribute_name, attribute_value in attribute_data.items():
            widget = self._data_widgets.get(attribute_name, None)
            if widget:
                widget.insert(0, attribute_value)

    def set_idref_list(self, idrefs: List[str]) -> None:
        """
        Updates the available options for all ID reference widgets.

        This method sets the given list of ID references as the selectable values 
        for all stored ID reference widgets, ensuring that they display the correct 
        choices based on the current application state.

        Args:
            idrefs (List[str]): A list of available ID references to populate the widgets.
        """
        for widget in self._idref_widgets:
            widget.config(values=idrefs)
