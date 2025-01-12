from mockclasses.mock_controller import MockController
from mockclasses.mock_models import MockComparisonModel, MockDocumentModel, MockTagModel
from model.configuration_model import ConfigurationModel
from utils.pdf_extraction_manager import PDFExtractionManager


test_pdf_path = "test_data/pdf"
test_docs = [
    "Grundwasser-Überwachungsprogramm - 2022.pdf",
    "Auf zu neuen Wegen – gemeinschaftlich und nachhaltig wirtschaften!_2022.pdf",
    "10274-Sondermessungen_2020_Abschlussbericht.pdf",
    "Energie-_und_Stoffstrommanagement._Praxisbeispiel_Kunststofflackierung.pdf",
]
DOCUMENT = 1
margins = [10, 10, 10, 10]
pages = "6-36"
text_model = MockDocumentModel()
tag_model = MockTagModel()
comparison_model = MockComparisonModel()
configuration_model = ConfigurationModel()

controller = MockController(
    document_model=text_model, comparison_model=comparison_model, configuration_model=configuration_model)
pdf_extractor = PDFExtractionManager(controller=controller,
                                     pdf_path=f"{test_pdf_path}/{test_docs[DOCUMENT]}", pages=pages)
