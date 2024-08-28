from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Label
from textual.widgets import Static
from textual.widgets import TabPane
from textual.widgets import TabbedContent


class AEBCommand(Static):

    HELP = """Press the button to change the AEB mode."""

    def compose(self) -> ComposeResult:
        with TabbedContent():
            for aeb_nr in 1, 2, 3, 4:
                with TabPane(f"AEB{aeb_nr}"):
                    with Horizontal():
                        yield Label("POWER")
                        yield Button("ON", id=f'btn-aeb{aeb_nr}-on', classes='command aeb power')
                        yield Button("OFF", id=f'btn-aeb{aeb_nr}-off', classes='command aeb power')
                    with Horizontal():
                        yield Label("MODE")
                        yield Button("INIT", id=f'btn-aeb{aeb_nr}-init', classes='command aeb init')
                        yield Button("CONFIG", id=f'btn-aeb{aeb_nr}-config', classes='command aeb config')
                        yield Button("IMAGE", id=f'btn-aeb{aeb_nr}-image', classes='command aeb image')
                        yield Button("PATTERN", id=f'btn-aeb{aeb_nr}-pattern', classes='command aeb pattern')
