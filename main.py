from controller.controller import Controller
from model.annotation_document_model import AnnotationDocumentModel
from model.annotation_mode_model import AnnotationModeModel
from model.appearance_model import AppearanceModel
from model.comparison_model import ComparisonModel
from model.configuration_model import ConfigurationModel
from model.extraction_document_model import ExtractionDocumentModel
from model.highlight_model import HighlightModel
from model.selection_model import SelectionModel
from view.main_window import MainWindow


def main():
    # Initialize model and controller
    preview_document_model = ExtractionDocumentModel()
    annotation_document_model = AnnotationDocumentModel()
    comparison_model = ComparisonModel()
    configuration_model = ConfigurationModel()
    selection_model = SelectionModel()
    appearance_model = AppearanceModel()
    annotation_mode_model = AnnotationModeModel()
    highlight_model = HighlightModel()

    controller = Controller(
        preview_document_model=preview_document_model, annotation_document_model=annotation_document_model,  comparison_model=comparison_model, selection_model=selection_model, configuration_model=configuration_model, appearance_model=appearance_model, annotation_mode_model=annotation_mode_model, highlight_model=highlight_model)
    app_view = MainWindow(controller)
    controller.finalize_views()
    controller.perform_create_color_scheme(colorset_name="viridis")
    #!DEBUG
    # testdoc = ["data/annotation/test_doc.json"]
    # controller.perform_open_file(testdoc)
    print("######### END INIT ###########")
    #!END DEBUG

    # Start the App
    app_view.mainloop()


# Entrypoint
if __name__ == "__main__":
    main()
