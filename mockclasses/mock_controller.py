from controller.interfaces import IController
from commands.interfaces import ICommand
from model.interfaces import IComparisonModel, IDocumentModel
from utils.interfaces import IObserver, IPublisher
from typing import List, Sequence


class MockController(IController):
    def __init__(self, text_model: IPublisher, tag_model: IPublisher):
        self.text_model = text_model
        self.tag_model = tag_model

    def execute_command(self, command: ICommand) -> None:
        """Executes the specified command."""
        print("Controller execute command")

    def undo(self, command: ICommand) -> None:
        """Reverses the actions of the specified command."""
        print("Controller undo command")

    def redo(self, command: ICommand) -> None:
        """Reapplies the actions of the specified command."""
        print("Controller redo command")

    def register_observer(self, observer: IObserver) -> None:
        print("Observer registered")

    def remove_observer(self, observer: IObserver) -> None:
        print("observer removed")

    def perform_text_selected(self, text: str) -> None:
        print(f"Text: {text} selected.")

    def get_template_groups(self) -> Sequence:
        """Returns the Groups of templates for the dynamic creation of Tagging menu frames """
        return [{"group_name": "Group1", "templates": [{
            "type": "TIMEX1",
            "attributes": {
                "tid": {
                    "active": True,
                    "type": "ID"
                },
                "type": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                },
                "functionInDocument": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["CREATION_TIME", "EXPIRATION_TIME", "MODIFICATION_TIME", "PUBLICATION_TIME", "RELEASE_TIME", "RECEPTION_TIME", "NONE"],
                    "default": "NONE"
                },
                "endPoint": {
                    "active": True,
                    "type": "IDREF"
                }
            }
        },
            {
            "type": "TIMEX2",
            "attributes": {
                "tid": {
                    "active": True,
                    "type": "ID"
                },
                "type": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                },
                "functionInDocument": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["CREATION_TIME", "EXPIRATION_TIME", "MODIFICATION_TIME", "PUBLICATION_TIME", "RELEASE_TIME", "RECEPTION_TIME", "NONE"],
                    "default": "NONE"
                },
                "beginPoint": {
                    "active": True,
                    "type": "IDREF"
                }
            }
        }]}, {"group_name": "Group2", "templates": [
            {
                "type": "TIMEX3",
                "attributes": {
                    "tid": {
                        "active": True,
                        "type": "ID"
                    },
                    "type": {
                        "active": True,
                        "type": "string",
                        "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                    },
                    "functionInDocument": {
                        "active": True,
                        "type": "string",
                        "allowedValues": ["A", "B", "C", "D", "E", "F", "G"],
                        "default": "NONE"
                    },
                    "anchorPoint": {
                        "active": True,
                        "type": "IDREF"
                    }
                }
            }
        ]}]

    def get_meta_tag_labels(self):
        return ["a-Tag", "b-Tag", "c-Tag"]

    def get_comparison_sentences(self) -> List[str]:
        """Retrieves the list of comparison sentences"""
        return ["Sentence 1", "sentence "]

    def get_update_data(self, publisher: IPublisher) -> None:
        if isinstance(publisher, IComparisonModel):
            return [f"This comes from {i+1}. comparison model" for i in range(3)]
        elif isinstance(publisher, IDocumentModel):
            return "This comes from document model\n"*100
        else:
            raise TypeError("Unsupported publisher type")
