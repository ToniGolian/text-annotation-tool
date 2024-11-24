from typing import Dict
from utils.interfaces import ILayoutPublisher


class MockConfigurationManager(ILayoutPublisher):
    def __init__(self):
        super().__init__()

    def get_layout_state(self) -> Dict:
        """Retrieves the layout state of the publisher."""
        tag_types = ["TagType A", "TagType B", "TagType C"]
        filenames = ["file a", "file b", "file c", "file d"]
        return {"tag_types": tag_types,
                "filenames": filenames,
                "num_files": len(filenames)}
