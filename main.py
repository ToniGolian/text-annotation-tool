from controller.controller import Controller
from model.configuration_model import ConfigurationModel
from view.main_window import MainWindow
from mockclasses.mock_models import MockDocumentModel, MockComparisonModel


def main():
    # Initialize model and controller
    text_model = MockDocumentModel()
    comparison_model = MockComparisonModel()
    configuration_model = ConfigurationModel()

    controller = Controller(
        document_model=text_model, comparison_model=comparison_model, configuration_model=configuration_model)
    app_view = MainWindow(controller)
    controller.finalize_views()

    # Start the App
    app_view.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()
