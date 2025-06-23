import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from controller.interfaces import IController
from data_classes.search_result import SearchResult
from view.tooltip import ToolTip


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
        # dict of attribute widgets to chose references to other tags
        self._idref_attributes = {}
        self._selected_text_entry = None  # Entry for selected text
        self._output_widget = None
        self._display_widget = None
        self._tooltips = []
        self._render()

    def _render(self) -> None:
        """
        Renders widgets for the tag based on the template, adding labels and entry or combobox widgets for each active attribute.
        """
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        row = 0
        self._name = self._template.get("type", "Tag")
        header_label = tk.Label(
            self, text=f"{self._name[0].upper()+self._name[1:]}-Tag", font=("Helvetica", 16))
        header_label.grid(row=row, column=0, columnspan=2,
                          padx=10, pady=(0, 10), sticky="w")
        row += 1

        is_db = self._template.get("db", False)
        if is_db:
            annotation_control_frame = tk.Frame(self)
            annotation_control_frame.grid(
                row=1, column=1, columnspan=2, pady=5, sticky="ew")

            start_annotation_button = ttk.Button(
                annotation_control_frame,
                text=f"Start {self._name} Annotation",
                command=self._button_pressed_start_db_annotation
            )
            start_annotation_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
            self._tooltips.append(ToolTip(
                start_annotation_button,
                f"The {self._name} annotation mode sequentially suggests all {self._name} expressions identified within the text."
            ))

            end_annotation_button = ttk.Button(
                annotation_control_frame,
                text=f"End {self._name} Annotation",
                command=self._button_pressed_end_db_annotation
            )
            end_annotation_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
            self._tooltips.append(ToolTip(
                end_annotation_button,
                f"Ends the {self._name} annotation mode. After ending, it's still possible to add {self._name} tags manually."
            ))

            navigation_control_frame = tk.Frame(self)
            navigation_control_frame.grid(
                row=2, column=1, columnspan=2, pady=5, sticky="ew")

            previous_suggestion_button = ttk.Button(
                navigation_control_frame,
                text="Previous",
                command=self._button_pressed_previous_db_suggestion_button
            )
            previous_suggestion_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
            self._tooltips.append(ToolTip(
                previous_suggestion_button,
                f"Previous {self._name} suggestion."
            ))

            next_suggestion_button = ttk.Button(
                navigation_control_frame,
                text="Next",
                command=self._button_pressed_next_db_suggestion_button
            )
            next_suggestion_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
            self._tooltips.append(ToolTip(
                next_suggestion_button,
                f"Next {self._name} suggestion."
            ))

            wrong_suggestion_button = ttk.Button(
                self,
                text="Mark wrong suggestion",
                command=self._button_pressed_mark_wrong_db_suggestion
            )
            wrong_suggestion_button.grid(
                row=3, column=1, sticky="ew", padx=5, pady=5)
            self._tooltips.append(ToolTip(
                wrong_suggestion_button,
                f"Marks the current suggestion as incorrect so it will no longer be suggested in the future."
            ))

            row = 4

        selected_text_label = tk.Label(self, text="Selected Text")
        selected_text_label.grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5)

        self._selected_text_entry = tk.Entry(self, state="disabled")
        self._selected_text_entry.grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        for attribute_name, attribute_data in self._template["attributes"].items():
            label = tk.Label(self, text=attribute_name)
            label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)

            attribute_type = attribute_data["type"].upper()

            if attribute_type in ["CDATA", "ID", "UNION"]:
                widget = tk.Entry(self)
            elif attribute_type == "OUTPUT":
                widget = tk.Entry(self, state="disabled")
                self._output_widget = widget
            elif attribute_type == "DISPLAY":
                widget = ttk.Combobox(self, values=[""])
                self._display_widget = widget
            else:
                allowed_values = [""] + attribute_data.get("allowedValues", [])
                widget = ttk.Combobox(self, values=allowed_values)
                widget.set(attribute_data.get(
                    "default", allowed_values[0] if allowed_values else ""))

            widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

            if attribute_type == "ID":
                attribute_name = "id"

            self._data_widgets[attribute_name] = widget
            if attribute_type == "IDREF":
                self._idref_attributes[attribute_name] = widget
                self._idref_widgets.append(widget)

            row += 1

        add_tag_button = ttk.Button(
            self, text="Add Tag", command=self._button_pressed_add_tag)
        add_tag_button.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        if not is_db:
            edit_label = tk.Label(self, text="ID to Edit")
            edit_label.grid(row=row, column=0, sticky="w",
                            padx=(15, 5), pady=5)

            self.edit_id_combobox = ttk.Combobox(self, values=[""])
            self._idref_widgets.append(self.edit_id_combobox)
            self.edit_id_combobox.grid(
                row=row, column=1, sticky="ew", padx=5, pady=5)
            row += 1

            edit_tag_button = ttk.Button(
                self, text="Edit Tag", command=self._button_pressed_edit_tag)
            edit_tag_button.grid(
                row=row, column=1, sticky="ew", padx=5, pady=5)
            row += 1

        delete_label = tk.Label(self, text="ID to Delete")
        delete_label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)

        self.delete_id_combobox = ttk.Combobox(self, values=[""])
        self._idref_widgets.append(self.delete_id_combobox)
        self.delete_id_combobox.grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

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
        Collects data from the tag creation widgets and returns it as a structured dictionary.

        The resulting dictionary includes:
            - "tag_type" (str): The type of the tag as specified in the template.
            - "attributes" (Dict[str, str]): A dictionary of attribute name-value pairs.
            - "position" (int): The position of the selected text in the document.
            - "text" (str): The selected text in the document.
            - "references" (Dict[str, str]): A dictionary mapping reference attributes to their target IDs.
            - "equivalent_uuids" (List[str]): A list of UUIDs that are considered equivalent (initially empty).
            - "uuid" (str): The tag's UUID (initially None; will be generated during insertion).

        Returns:
            dict: A dictionary containing all data required to construct a tag.

        Raises:
            ValueError: If no text is currently selected in the document.
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

        references = {
            attribute_name: widget.get().strip()
            for attribute_name, widget in self._idref_attributes.items()
            if widget.get().strip()
        }

        # Build the tag data dictionary
        tag_data = {
            "tag_type": self._template.get("type", "Tag"),
            "attributes": attributes,
            "position": position,
            "text": selected_text,
            "references": references,
            "equivalent_uuids": [],
            "uuid:": None
        }

        return tag_data

    def get_name(self) -> str:
        """
        Retrieves the name of the menu frame.


        Returns:
            str: The name of the  menu frame.
        """
        return self._name

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

    def set_search_result(self, search_result: SearchResult) -> None:
        """
        Sets the search result for the tag type.

        This method updates the search result widget with the provided search result,
        ensuring that it reflects the current state of the tag type.

        Args:
            search_result (SearchResult): The search result to set for the tag type.
        """
        self._current_search_result = search_result
        if self._display_widget:
            self._display_widget.config(state="normal")
            self._display_widget.delete(0, tk.END)
            if search_result and search_result.get_display_list():
                self._display_widget.set(search_result.get_display_list()[0])

            else:
                self._display_widget.set("")
            self._display_widget.config(state="readonly")
        if self._output_widget:
            self._output_widget.config(state="normal")
            self._output_widget.delete(0, tk.END)
            if search_result and search_result.get_display_list():
                self._output_widget.insert(
                    0, search_result.get_output_for_display(self._display_widget.get()))
            else:
                self._output_widget.set("")
            self._output_widget.config(state="disabled")

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

    def _button_pressed_start_db_annotation(self) -> None:
        """
        Handles the event when the start annotation button is pressed.
        Initiates the annotation process for the current tag type.
        """
        self._controller.perform_start_db_annotation(
            tag_type=self._name, caller_id=self._root_view_id)

    def _button_pressed_end_db_annotation(self) -> None:
        """
        Handles the event when the end annotation button is pressed.
        Ends the annotation process for the current tag type.
        """
        self._controller.perform_end_db_annotation()

    def _button_pressed_previous_db_suggestion_button(self) -> None:
        """
        Handles the event when the previous suggestion button is pressed.
        Requests the controller to show the previous suggestion for the tag type.
        """
        self._controller.perform_previous_suggestion()

    def _button_pressed_next_db_suggestion_button(self) -> None:
        """
        Handles the event when the next suggestion button is pressed.
        Requests the controller to show the next suggestion for the tag type.
        """
        self._controller.perform_next_suggestion()

    def _button_pressed_mark_wrong_db_suggestion(self) -> None:
        """
        Handles the event when the mark-as-wrong-suggestion button is pressed.
        Informs the controller that the current suggestion should not be shown again.
        """
        self._controller.perform_mark_wrong_db_suggestion(
            tag_type=self._name)
