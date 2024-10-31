# from model.text_model import TextModel
# from model.tag_model import TagModel
from view.main_window import MainWindow
# from controller.controller import Controller
import tkinter as tk
from mockclasses.mock_models import MockTagModel,MockTextModel
from mockclasses.mock_controller import MockController

def main():
    #Initialize the tk window

    # Initialize model and controller
    text_model = MockTextModel()
    tag_model = MockTagModel()
    controller = MockController(text_model, tag_model)

    app = MainWindow(controller=controller)
    app.mainloop()

# Entrypoint
if __name__ == "__main__":
    main()
