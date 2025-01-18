from controller.controller import Controller
from mockclasses.mock_controller import MockController
from mockclasses.mock_list_manager import ListManager
from mockclasses.mock_models import MockComparisonModel, MockDocumentModel, MockTagModel
from model.annotation_document_model import AnnotationDocumentModel
from model.comparison_document_model import ComparisonDocumentModel
from model.configuration_model import ConfigurationModel
from model.preview_document_model import PreviewDocumentModel
from model.selection_model import SelectionModel
from utils.pdf_extraction_manager import PDFExtractionManager


test_pdf_path = "test_data/pdf"
test_docs = [
    "Grundwasser-Überwachungsprogramm - 2022.pdf",
    "Auf zu neuen Wegen – gemeinschaftlich und nachhaltig wirtschaften!_2022.pdf",
    "10274-Sondermessungen_2020_Abschlussbericht.pdf",
    "Energie-_und_Stoffstrommanagement._Praxisbeispiel_Kunststofflackierung.pdf",
    "Energie-_und_Stoffstrommanagement._Praxisbeispiel_Kunststofflackierung.pdf"
]
DOCUMENT = 4
margins = [10, 10, 10, 10]
pages = "6-36"
preview_document_model = PreviewDocumentModel()
annotation_document_model = AnnotationDocumentModel()
comparison_document_model = ComparisonDocumentModel()
comparison_model = MockComparisonModel()
configuration_model = ConfigurationModel()
selection_model = SelectionModel()

controller = Controller(
    preview_document_model=preview_document_model, annotation_document_model=annotation_document_model, comparison_document_model=comparison_document_model, comparison_model=comparison_model, selection_model=selection_model, configuration_model=configuration_model)
list_manager = ListManager()

pdf_extractor = PDFExtractionManager(list_manager=list_manager,
                                     pdf_path=f"{test_pdf_path}/{test_docs[DOCUMENT]}", pages=pages)
extraction_data = {"pdf_path": f"{test_pdf_path}/{test_docs[DOCUMENT]}"}
pdf_extractor.extract_document(extraction_data)
