from controller.interfaces import IController
from commands.interfaces import ICommand
from model.interfaces import ITextModel,ITagModel

class MockController(IController):
    def __init__(self,text_model:ITextModel,tag_model:ITagModel):
        self.text_model=text_model
        self.tag_model=tag_model
        
    def execute_command(self, command: ICommand) -> None:
        """Executes the specified command."""
        print("Controller execute command")

    def undo(self, command: ICommand) -> None:
        """Reverses the actions of the specified command."""
        print("Controller undo command")

    def redo(self, command: ICommand) -> None:
        """Reapplies the actions of the specified command."""
        print("Controller redo command")
