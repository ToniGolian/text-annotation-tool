from controller.controller import Controller
from model.configuration_model import ConfigurationModel
from view.main_window import MainWindow
from mockclasses.mock_configuration_model import MockConfigurationModel
from mockclasses.mock_models import MockTagModel, MockDocumentModel, MockComparisonModel
from mockclasses.mock_controller import MockController


def main():
    # Initialize model and controller
    text_model = MockDocumentModel()
    tag_model = MockTagModel()
    comparison_model = MockComparisonModel()
    configuration_model = ConfigurationModel()
    controller = MockController(
        document_model=text_model, comparison_model=comparison_model, configuration_model=configuration_model)
    app_view = MainWindow(controller)
    controller.finalize_views()

    # Start the App
    app_view.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()
