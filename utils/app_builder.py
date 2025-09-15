
from controller.controller import Controller
from model.annotation_document_model import AnnotationDocumentModel
from model.annotation_mode_model import AnnotationModeModel
from model.comparison_model import ComparisonModel
from model.extraction_document_model import ExtractionDocumentModel
from model.global_settings_model import GlobalSettingsModel
from model.highlight_model import HighlightModel
from model.layout_configuration_model import LayoutConfigurationModel
from model.project_settings_model import ProjectSettingsModel
from model.project_wizard_model import ProjectWizardModel
from model.save_state_model import SaveStateModel
from model.selection_model import SelectionModel
from view.main_window import MainWindow


class AppBuilder:
    def build_app(self) -> MainWindow:
        """
        Build the main application window.
        Returns:
            MainWindow: The main application window instance.
        """
        # Initialize model and controller
        print("######### START INIT ###########")
        print("Initializing models")
        preview_document_model = ExtractionDocumentModel()
        annotation_document_model = AnnotationDocumentModel()
        comparison_model = ComparisonModel()
        configuration_model = LayoutConfigurationModel()
        selection_model = SelectionModel()
        annotation_mode_model = AnnotationModeModel()
        highlight_model = HighlightModel()
        save_state_model = SaveStateModel()
        project_wizard_model = ProjectWizardModel()
        global_settings_model = GlobalSettingsModel()
        project_settings_model = ProjectSettingsModel()

        print("Creating controller")
        controller = Controller(
            preview_document_model=preview_document_model, annotation_document_model=annotation_document_model,  comparison_model=comparison_model, selection_model=selection_model, layout_configuration_model=configuration_model, annotation_mode_model=annotation_mode_model, highlight_model=highlight_model, save_state_model=save_state_model, project_wizard_model=project_wizard_model, global_settings_model=global_settings_model, project_settings_model=project_settings_model)
        print("Initializing views")
        app_view = MainWindow(controller)
        print("Finalizing controller")
        controller.perform_project_load_project()
        print("######### END INIT ###########")
        return app_view
