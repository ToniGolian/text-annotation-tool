from view.main_window import MainWindow
from mockclasses.mock_configuration_manager import MockConfigurationManager
from mockclasses.mock_models import MockTagModel, MockDocumentModel, MockComparisonModel
from mockclasses.mock_controller import MockController


def main():
    # Initialize model and controller
    text_model = MockDocumentModel()
    tag_model = MockTagModel()
    comparison_model = MockComparisonModel()
    configuration_manager = MockConfigurationManager()
    controller = MockController(
        text_model=text_model, comparison_model=comparison_model, configuration_manager=configuration_manager)
    app_view = MainWindow(controller)
    controller.finalize_views()

    # Start the App
    app_view.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()
