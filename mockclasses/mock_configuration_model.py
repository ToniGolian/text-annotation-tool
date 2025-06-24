from typing import Dict
from model.interfaces import ILayoutConfigurationModel


class MockConfigurationModel(ILayoutConfigurationModel):
    def __init__(self):
        super().__init__()
        self.tag_types = ["TagType A", "TagType B", "TagType C"]
        self.file_names = ["file a", "file b", "file c", "file d"]
        self.template_groups = [{"group_name": "Group1", "templates": [{
            "type": "TIMEX3",
            "attributes": {
                "tid": {
                    "type": "ID"
                },
                "type": {
                    "type": "string",
                    "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                },
                "functionInDocument": {
                    "type": "string",
                    "allowedValues": ["CREATION_TIME", "EXPIRATION_TIME", "MODIFICATION_TIME", "PUBLICATION_TIME", "RELEASE_TIME", "RECEPTION_TIME", "NONE"],
                    "default": "NONE"
                },
                "beginPoint": {
                    "type": "IDREF"
                },
                "endPoint": {
                    "type": "IDREF"
                },
                "quant": {
                    "type": "CDATA"
                },
                "freq": {
                    "type": "Duration"
                },
                "temporalFunction": {
                    "type": "boolean",
                    "allowedValues": ["true", "false"],
                    "default": "false"
                },
                "value": {
                    "type": "union",
                    "allowedValues": ["Duration", "Date", "Time", "WeekDate", "WeekTime", "Season", "PartOfYear", "PaPrFu"]
                },
                "valueFromFunction": {
                    "type": "IDREF"
                },
                "mod": {
                    "type": "string",
                    "allowedValues": ["BEFORE", "AFTER", "ON_OR_BEFORE", "ON_OR_AFTER", "LESS_THAN", "MORE_THAN", "EQUAL_OR_LESS", "EQUAL_OR_MORE", "START", "MID", "END", "APPROX"]
                },
                "anchorTimeID": {
                    "type": "IDREF"
                },
                "comment": {
                    "type": "CDATA"
                }
            }
        },
            {
            "type": "TLINK",

            "attributes": {
                "lid": {
                    "type": "ID"
                },
                "origin": {
                    "type": "CDATA"
                },
                "eventInstanceID": {
                    "type": "IDREF"
                },
                "timeID": {
                    "type": "IDREF"
                },
                "signalID": {
                    "type": "IDREF"
                },
                "relatedToEventInstance": {
                    "type": "IDREF"
                },
                "relatedToTime": {
                    "type": "IDREF"
                },
                "relType": {
                    "type": "string",
                    "allowedValues": ["BEFORE", "AFTER", "INCLUDES", "IS_INCLUDED", "DURING", "SIMULTANEOUS", "IAFTER", "IBEFORE", "IDENTITY", "BEGINS", "ENDS", "BEGUN_BY", "ENDED_BY", "DURING_INV"]
                },
                "comment": {
                    "type": "CDATA"
                },
                "syntax": {
                    "type": "CDATA"
                }
            }
        }
        ]}, {"group_name": "Group2", "templates": [
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

    def get_layout_state(self) -> Dict:
        """Retrieves the layout state of the publisher."""
        return {"tag_types": self.tag_types,
                "file_names": self.file_names,
                "num_files": len(self.file_names),
                "template_groups": self.template_groups}
