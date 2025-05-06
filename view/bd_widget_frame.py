import tkinter as tk
from tkinter import ttk

from view.interfaces import IDBWidgetFrame
from view.tooltip import ToolTip


class DBWidgetFrame(tk.Frame, IDBWidgetFrame):
    def __init__(self):
        self._tag_type = None

        self._render()

    def _render(self):
        start_annotation_button = ttk.Button(
            self, text=f"Start {self._tag_type} annotation", command=self.on_button_pressed_start_annotation)
        start_annotation_button.grid(
            row=1, column=1, columnspan=1, pady=5, sticky="ew")
        self.tooltips.append(ToolTip(start_annotation_button,
                                     f"The {self._tag_type} annotation mode sequentially suggests all {self._tag_type} expressions identified within the text."))

        end_annotation_button = ttk.Button(
            self, text="End {self._tag_type} annotation", command=self.on_button_pressed_end_annotation)
        end_annotation_button.grid(
            row=1, column=2, columnspan=1, pady=5, sticky="ew")
        self.tooltips.append(ToolTip(end_annotation_button,
                                     "Ends the {self._tag_type} annotation mode. After ending, it's still possible to add {self._tag_type} tags manually."))

        previous_suggestion_button = ttk.Button(
            self, text="Previous", command=self.on_button_pressed_previous_suggestion_button)
        previous_suggestion_button.grid(
            row=2, column=1, columnspan=1, pady=5, sticky="ew")
        self.tooltips.append(ToolTip(previous_suggestion_button,
                                     "Previous Geo Tag suggestion."))

        next_suggestion_button = ttk.Button(
            self, text="Next", command=self.on_button_pressed_next_suggestion_button)
        next_suggestion_button.grid(
            row=2, column=2, columnspan=1, pady=5, sticky="ew")
        self.tooltips.append(ToolTip(next_suggestion_button,
                                     "Next Geo Tag suggestion."))

        # todo continue here

        tk.Label(self, text="Selected Text").grid(
            row=3, column=0, padx=5, sticky="e")
        self.widget_selected_text_geo = tk.Entry(self, state="disabled")
        self.widget_selected_text_geo.grid(
            row=3, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        tk.Label(self, text="TID").grid(
            row=4, column=0, padx=5, sticky="e")
        self.widget_tid_geo = tk.Entry(self)
        self.widget_tid_geo.grid(
            row=4, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

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
            '<<ComboboxSelected>>', self.combobox_selected_geo_hierarchy)

        add_geo_tag_button = ttk.Button(
            self, text="Add Geo Tag", command=self.on_button_pressed_add_geo_tag)
        add_geo_tag_button.grid(
            row=7, column=1, columnspan=2, pady=5, sticky="ew")
        self.tooltips.append(
            ToolTip(add_geo_tag_button, "Adds a geo tag with the chosen attributes."))
        add_geo_tag_button = ttk.Button(
            self, text="Mark as wrong suggestion", command=self.on_button_pressed_mark_wrong_suggestion)
        add_geo_tag_button.grid(
            row=8, column=1, columnspan=2, pady=5, sticky="ew")
        self.tooltips.append(ToolTip(
            add_geo_tag_button, "Mark this suggestion as incorrect to ensure it is not recommended again in the future."))

    def update(self):
        raise NotImplementedError()
