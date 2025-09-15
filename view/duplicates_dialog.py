import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any


class DuplicatesDialog(tk.Toplevel):
    """
    Dialog showing duplicate tags with rename entries. Content is scrollable.

    Args:
        duplicates: Mapping from group name to list of tag dicts
                    each with keys "display_name" and "name".
        master: Optional parent window.
    """

    def __init__(self, duplicates: Dict[str, List[Dict[str, Any]]], master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("Duplicate Tags Found")
        self.geometry("600x400")
        self._duplicates = duplicates
        self._create_widgets()
        self._set_close_protocol()

        self.result = None

    def show(self) -> List[Dict[str, Any]] | None:
        """
        Make the dialog modal and wait until it is closed.

        Returns:
            The result set by the OK button, or None if canceled/closed.
        """
        # Set transient only if master is visible
        try:
            if self.master is not None and self.master.state() != "withdrawn":
                self.transient(self.master)
        except tk.TclError:
            pass

        self.deiconify()        # Ensure the dialog is visible
        self.focus_set()        # Focus the dialog
        self.grab_set()         # Make modal
        self.wait_visibility()  # Ensure it is mapped before waiting
        self.wait_window()      # Block until window is destroyed
        return self.result

    def _create_widgets(self) -> None:
        """Build UI with a canvas + vertical scrollbar. Rows expand horizontally."""
        # Canvas + scrollbar
        canvas = tk.Canvas(self, highlightthickness=0)
        vbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")

        # Let the canvas expand with the toplevel
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Inner content frame inside the canvas
        content = tk.Frame(canvas)
        content_id = canvas.create_window((0, 0), window=content, anchor="nw")

        # Ensure the inner frame always matches canvas width (so children can stretch)
        def _sync_inner_width(event: tk.Event) -> None:
            canvas.itemconfigure(content_id, width=canvas.winfo_width())
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _sync_inner_width)
        content.bind("<Configure>", lambda _e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        # Allow widgets in column 0 to expand horizontally
        content.columnconfigure(0, weight=1)

        row = 0
        label = ttk.Label(
            content, text="Some tags share similar names.", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, sticky="w", padx=10, pady=(0, 10))
        row += 1
        label = ttk.Label(
            content, text="Please rename them:", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, sticky="w", padx=10, pady=(0, 10))
        row += 1
        for name, tag_list in self._duplicates.items():
            # Section header
            label = ttk.Label(content, text=name,
                              font=("Helvetica", 10, "bold"))
            label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 2))
            row += 1

            # Red frame for the tag rows (fills width)
            frame = tk.Frame(content)
            frame.grid(row=row, column=0, sticky="ew", padx=10, pady=(0, 10))
            # Make entry column stretch
            frame.columnconfigure(1, weight=1)
            row += 1

            label = ttk.Label(frame, text="Tag")
            label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
            label = ttk.Label(frame, text="New Name")
            label.grid(row=0, column=1, sticky="ew", pady=(0, 5))
            label = ttk.Label(frame, text="Id Prefix")
            label.grid(row=0, column=2, sticky="ew", pady=(0, 5))
            for i, tag in enumerate(tag_list):
                ttk.Label(frame, text=tag["display_name"]).grid(
                    row=i+1, column=0, sticky="w", padx=(0, 10)
                )
                entry = ttk.Entry(frame)
                # Store name entry ref for later retrieval
                tag["name_entry"] = entry
                entry.insert(0, tag["name"])
                entry.grid(row=i+1, column=1, sticky="ew", padx=(0, 5))
                entry = ttk.Entry(frame)
                # Store id prefix entry ref for later retrieval
                tag["id_prefix_entry"] = entry
                entry.insert(0, tag.get("id_prefix", ""))
                entry.grid(row=i+1, column=2, sticky="ew")

        # Button row (fills width)
        button_frame = ttk.Frame(content)
        button_frame.grid(row=row, column=0, sticky="ew",
                          padx=10, pady=(10, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="OK", command=self._on_button_pressed_ok).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(button_frame, text="Cancel", command=self._on_button_pressed_cancel).grid(
            row=0, column=1, sticky="ew", padx=(5, 0)
        )

    def _set_close_protocol(self) -> None:
        """Close the dialog when clicking the window manager close button."""
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _on_button_pressed_ok(self) -> None:
        """
        Handles the OK button press event.
        """
        result = []
        for _, tags in self._duplicates.items():
            for tag in tags:
                tag["name"] = tag["name_entry"].get().strip()
                tag["id_prefix"] = tag["id_prefix_entry"].get().strip()
                result.append(tag)
        self.result = result
        self.destroy()

    def _on_button_pressed_cancel(self) -> None:
        """
        Handles the Cancel button press event.
        """
        self.result = None
        self.destroy()
