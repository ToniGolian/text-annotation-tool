# from model.text_model import TextModel
# from model.tag_model import TagModel
from view.main_window import MainWindow
# from controller.controller import Controller
import tkinter as tk
from mockclasses.mock_models import MockTagModel, MockDocumentModel, MockComparisonModel
from mockclasses.mock_controller import MockController


def main():
    # Initialize model and controller
    text_model = MockDocumentModel()
    tag_model = MockTagModel()
    comparison_model = MockComparisonModel()
    controller = MockController(text_model, comparison_model)
    app_view = MainWindow(controller)
    controller.finalize_views()

    # Start the App
    app_view.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()
