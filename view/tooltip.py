
import tkinter as tk


class ToolTip:
    """
    A class to create a tooltip that appears when hovering over a tkinter widget.

    Attributes:
    - widget: The widget to which the tooltip is attached.
    - text: The text displayed by the tooltip.
    - waittime: The delay before the tooltip appears after hovering.
    - wraplength: The maximum line width of the tooltip. Longer text wraps to a new line.
    """

    def __init__(self, widget, text='widget info', waittime=400, wraplength=250):
        """
        Initializes the tooltip with a widget and text.

        Parameters:
        - widget: The widget the tooltip is attached to.
        - text (str, optional): The text displayed by the tooltip. Defaults to 'widget info'.
        - waittime (int, optional): The delay before the tooltip appears in milliseconds. Defaults to 400.
        - wraplength (int, optional): The maximum line width of the tooltip in pixels. Defaults to 250.
        """
        self.widget = widget
        self.text = text
        self.waittime = waittime
        self.wraplength = wraplength
        self.id = None
        self.tw = None
        self.activate()

    def activate(self):
        """
        Activates the tooltip, making it visible when hovering over the widget.
        """
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def deactivate(self):
        """
        Deactivates the tooltip, making it invisible regardless of mouse movement.
        """
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
        self.hide_tooltip()

    def show_tooltip(self, event=None):
        """
        Displays the tooltip at the mouse position after a delay.

        Parameters:
        - event: The event that triggered this method. Defaults to None.
        """
        def create_tooltip_window():
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            self.tw = tk.Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tw, text=self.text, justify='left',
                             background="#ffffe0", relief='solid', borderwidth=1,
                             wraplength=self.wraplength)
            label.pack(ipadx=1)

        self.id = self.widget.after(self.waittime, create_tooltip_window)

    def hide_tooltip(self, event=None):
        """
        Hides the tooltip window.

        Parameters:
        - event: The event that triggered this method. Defaults to None.
        """
        if self.tw:
            self.tw.destroy()
        self.tw = None
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = None
