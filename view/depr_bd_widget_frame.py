import tkinter as tk
from tkinter import ttk

from view.interfaces import IDBWidgetFrame
from view.tooltip import ToolTip


class DBWidgetFrame(tk.Frame, IDBWidgetFrame):
    def __init__(self, parent: tk.Widget,  tag_type: str, id_prefix: str) -> None:
        super().__init__(parent)
        self._tag_type = tag_type
        self._id_prefix = id_prefix
        self._tooltips = []
        self._render()

    def _render(self):
        start_annotation_button = ttk.Button(
            self, text=f"Start {self._tag_type} annotation", command=self._on_button_pressed_start_annotation)
        start_annotation_button.grid(
            row=1, column=1, columnspan=1, pady=5, sticky="ew")
        self._tooltips.append(ToolTip(start_annotation_button,
                                      f"The {self._tag_type} annotation mode sequentially suggests all {self._tag_type} expressions identified within the text."))

        end_annotation_button = ttk.Button(
            self, text=f"End {self._tag_type} annotation", command=self._on_button_pressed_end_annotation)
        end_annotation_button.grid(
            row=1, column=2, columnspan=1, pady=5, sticky="ew")
        self._tooltips.append(ToolTip(end_annotation_button,
                                      f"Ends the {self._tag_type} annotation mode. After ending, it's still possible to add {self._tag_type} tags manually."))

        previous_suggestion_button = ttk.Button(
            self, text="Previous", command=self._on_button_pressed_previous_suggestion_button)
        previous_suggestion_button.grid(
            row=2, column=1, columnspan=1, pady=5, sticky="ew")
        self._tooltips.append(ToolTip(previous_suggestion_button,
                                      f"Previous {self._tag_type} suggestion."))

        next_suggestion_button = ttk.Button(
            self, text="Next", command=self._on_button_pressed_next_suggestion_button)
        next_suggestion_button.grid(
            row=2, column=2, columnspan=1, pady=5, sticky="ew")
        self._tooltips.append(ToolTip(next_suggestion_button,
                                      f"Next {self._tag_type} suggestion."))

        tk.Label(self, text="Selected Text").grid(
            row=3, column=0, padx=5, sticky="e")
        self.widget_selected_text_geo = tk.Entry(self, state="disabled")
        self.widget_selected_text_geo.grid(
            row=3, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        tk.Label(self, text=f"{self._id_prefix.upper()}ID").grid(
            row=4, column=0, padx=5, sticky="e")
        self.widget_tid_geo = tk.Entry(self)
        self.widget_tid_geo.grid(
            row=4, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        # todo continue here

        tk.Label(self, text="NNID").grid(
            row=5, column=0, padx=5, sticky="e")
        self.widget_nnid_geo = tk.Entry(self)
        self.widget_nnid_geo.grid(
            row=5, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        tk.Label(self, text="Hierarchy").grid(
            row=6, column=0, padx=5, sticky="e")
        self.widget_hierarchy_geo = ttk.Combobox(
            self, values=[])
        self.widget_hierarchy_geo.grid(
            row=6, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        self.widget_hierarchy_geo.bind(
            '<<ComboboxSelected>>', self._combobox_selected_geo_hierarchy)

        add_geo_tag_button = ttk.Button(
            self, text="Add Geo Tag", command=self._on_button_pressed_add_tag)
        add_geo_tag_button.grid(
            row=7, column=1, columnspan=2, pady=5, sticky="ew")
        self._tooltips.append(
            ToolTip(add_geo_tag_button, "Adds a geo tag with the chosen attributes."))
        add_geo_tag_button = ttk.Button(
            self, text="Mark as wrong suggestion", command=self._on_button_pressed_mark_wrong_suggestion)
        add_geo_tag_button.grid(
            row=8, column=1, columnspan=2, pady=5, sticky="ew")
        self._tooltips.append(ToolTip(
            add_geo_tag_button, "Mark this suggestion as incorrect to ensure it is not recommended again in the future."))

    def update(self):
        raise NotImplementedError()

    def _on_button_pressed_start_annotation(self) -> None:
        pass

    def _on_button_pressed_end_annotation(self) -> None:
        pass

    def _on_button_pressed_previous_suggestion_button(self) -> None:
        pass

    def _on_button_pressed_next_suggestion_button(self) -> None:
        pass

    def _on_button_pressed_add_tag(self) -> None:
        pass

    def _on_button_pressed_mark_wrong_suggestion(self) -> None:
        pass

    def _combobox_selected_geo_hierarchy(self, event) -> None:
        pass
