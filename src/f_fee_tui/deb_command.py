from textual.app import ComposeResult
from textual.widgets import Button
from textual.widgets import Static


class DEBCommand(Static):

    HELP = """Press the button to change the DEB mode."""

    def compose(self) -> ComposeResult:
        yield Button("ON", id='btn-deb-on', classes='command')
        yield Button("FULL IMAGE PATTERN", id='btn-deb-full-image-pattern', classes='command')
        yield Button("STANDBY", id='btn-deb-standby', classes='command')
        yield Button("FULL IMAGE", id='btn-deb-full-image', classes='command')
        yield Button("IMMEDIATE ON", id='btn-deb-immediate-on', classes='command')
