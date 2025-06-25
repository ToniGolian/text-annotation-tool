import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from observer.interfaces import IObserver, IPublisher
from view.tooltip import ToolTip


class SearchFrame(tk.Frame, IObserver):
    def __init__(self, parent: tk.Widget, controller: IController, root_view_id: str) -> None:
        """
        Initializes the SearchFrame with a search entry and option buttons.

        Args:
            parent (tk.Widget): The parent widget.
            controller (IController): The controller for coordinating search actions.
            root_view_id (str): Identifier for the root view, used for search context.
        """
        super().__init__(parent)
        self._controller = controller
        self._root_view_id = root_view_id

        self._view_id = f"{root_view_id}_search"
        self._controller.add_observer(self)
        self._controller.register_view(self._view_id, self)

        self._label = ttk.Label(self, text="Search:")

        self._entry = ttk.Entry(self)
        self._entry.bind("<KeyRelease>", self._on_key_pressed)
        self._debounce_after_id = None

        self._button_frame = ttk.Frame(self)

        # Variable declarations
        self._case_var = tk.BooleanVar(value=False)
        self._whole_word_var = tk.BooleanVar(value=False)
        self._regex_var = tk.BooleanVar(value=False)

        # Checkbox Buttons
        self._case_button = ttk.Checkbutton(
            self._button_frame, text="Aa", variable=self._case_var)
        ToolTip(self._case_button,
                text="Case-sensitive search.\nMatches only exact upper/lowercase.")

        self._whole_word_button = ttk.Checkbutton(
            self._button_frame, text="|ab|", variable=self._whole_word_var)
        ToolTip(self._whole_word_button,
                text="Whole word match.\nMatches only complete tokens.")

        self._regex_button = ttk.Checkbutton(
            self._button_frame, text="□*", variable=self._regex_var)
        ToolTip(self._regex_button,
                text="Regex mode.\nInterpret search term as a regular expression.")

        # Trigger search immediately when any checkbox changes
        self._case_var.trace_add("write", lambda *args: self._trigger_search())
        self._whole_word_var.trace_add(
            "write", lambda *args: self._trigger_search())
        self._regex_var.trace_add(
            "write", lambda *args: self._trigger_search())

        # Variables for search result info
        self._index_var = tk.IntVar(value=0)
        self._num_var = tk.IntVar(value=0)

        # Info frame between search options and navigation
        self._info_frame = ttk.Frame(self)
        self._info_text_var = tk.StringVar()
        self._info_label = ttk.Label(
            self._info_frame, textvariable=self._info_text_var)
        self._info_label.pack(side=tk.LEFT, padx=2)

        # Automatically update info text when variables change
        self._index_var.trace_add(
            "write", lambda *args: self._update_info_label())
        self._num_var.trace_add(
            "write", lambda *args: self._update_info_label())
        self._update_info_label()

        # Navigation buttons
        self._next_prev_frame = ttk.Frame(self)
        self._prev_button = ttk.Button(
            self._next_prev_frame, text="<", command=lambda: self._controller.perform_previous_suggestion())
        self._next_button = ttk.Button(
            self._next_prev_frame, text=">", command=lambda: self._controller.perform_next_suggestion())
        self._prev_button.pack(side=tk.LEFT, padx=2)
        self._next_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self._prev_button, text="Go to previous search result.")
        ToolTip(self._next_button, text="Go to next search result.")

        self._render()

    def _render(self) -> None:
        """
        Renders and arranges the widgets within the frame.
        """
        self.grid_columnconfigure(1, weight=1)  # Entry expands horizontally

        self._label.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="w")
        self._entry.grid(row=0, column=1, padx=2, pady=5, sticky="ew")

        self._button_frame.grid(
            row=0, column=2, padx=(2, 5), pady=5, sticky="e")
        for i, button in enumerate([self._case_button, self._whole_word_button, self._regex_button]):
            button.grid(row=0, column=i, padx=1)
            # button.configure(width=4)

        self._info_frame.grid(row=0, column=3, padx=(2, 5), pady=5, sticky="e")
        self._next_prev_frame.grid(
            row=0, column=4, padx=(2, 5), pady=5, sticky="e")

    def _on_key_pressed(self, event) -> None:
        """
        Triggers search with debouncing when user types in the search entry.

        Args:
            event: Tkinter event object from the keypress.
        """
        if self._debounce_after_id:
            self.after_cancel(self._debounce_after_id)

        self._debounce_after_id = self.after(300, self._trigger_search)

    def _trigger_search(self) -> None:
        """
        Extracts search parameters and delegates the search to the controller.
        """
        search_term = self._entry.get()
        if not search_term:
            self._controller.perform_end_search()
            return
        options = {
            "search_term": search_term,
            "case_sensitive": self._case_var.get(),
            "whole_word": self._whole_word_var.get(),
            "regex": self._regex_var.get()
        }
        self._controller.perform_manual_search(
            search_options=options, caller_id=self._root_view_id)

    def reset_entry(self) -> None:
        """
        Resets the search entry and all related options.
        """
        self._entry.delete(0, tk.END)
        self._case_var.set(False)
        self._whole_word_var.set(False)
        self._regex_var.set(False)
        self._index_var.set(0)
        self._num_var.set(0)

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the search frame with the current observer state from the controller.
        """
        state = self._controller.get_observer_state(
            observer=self, publisher=publisher)
        index = state.get("index", 0)
        num_results = state.get("num_results", 0)
        self._index_var.set(index+1)
        self._num_var.set(num_results)
        self._update_info_label

    def _update_info_label(self) -> None:
        """
        Updates the text of the info label to show current index/total.
        """
        self._info_text_var.set(
            f"{self._index_var.get()}/{self._num_var.get()}")
