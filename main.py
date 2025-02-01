from controller.controller import Controller
from mockclasses.mock_configuration_model import MockConfigurationModel
from model.annotation_document_model import AnnotationDocumentModel
from model.comparison_document_model import ComparisonDocumentModel
from model.configuration_model import ConfigurationModel
from model.extraction_document_model import ExtractionDocumentModel
from model.selection_model import SelectionModel
from view.main_window import MainWindow
from mockclasses.mock_models import MockDocumentModel, MockComparisonModel


def main():
    # Initialize model and controller
    preview_document_model = ExtractionDocumentModel()
    annotation_document_model = AnnotationDocumentModel()
    comparison_document_model = ComparisonDocumentModel()
    comparison_model = MockComparisonModel()
    configuration_model = ConfigurationModel()
    selection_model = SelectionModel()

    controller = Controller(
        preview_document_model=preview_document_model, annotation_document_model=annotation_document_model, comparison_document_model=comparison_document_model, comparison_model=comparison_model, selection_model=selection_model, configuration_model=configuration_model)
    app_view = MainWindow(controller)
    controller.finalize_views()
    #!DEBUG
    annotation_document_model.notify_observers()
    print("######### END INIT ###########")
    #!END DEBUG

    # Start the App
    app_view.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()
