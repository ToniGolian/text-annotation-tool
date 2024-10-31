# main.py

from model.text_model import TextModel
from model.tag_model import TagModel
from view.main_frame import Frame
from controller.controller import Controller
import tkinter as tk

def main():
    #Initialize the tk window
    root = tk.Tk()
    root.title("Text Annotation Tool")

    # Initialize model and controller
    text_model = TextModel()
    tag_model = TagModel()
    controller = Controller(text_model, tag_model)

    # Initialize view
    main_frame = Frame(root, controller)
    main_frame.pack()

    # Start the main loop
    root.mainloop()

# Entrypoint
if __name__ == "__main__":
    main()
