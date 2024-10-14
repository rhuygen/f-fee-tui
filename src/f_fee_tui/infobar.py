from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label

from f_fee_tui.services import services


class InfoBar(Horizontal):

    DEFAULT_CSS = """
    InfoBar {
        height: 1;
        dock: bottom;
        Label {
            margin: 0 1 0 0; 
        }
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self._names = services

    def compose(self) -> ComposeResult:
        for name in self._names:
            yield Label(name, id=name)
            yield Label("🔴", id=f"{name}_active", classes="status")

    def on_mount(self, event: events.Mount) -> None:

        for name, props in services.items():
            lbl = self.query_one(f"#{name}", Label)
            tooltip = props.get('description', '')
            self.app.log(f"Added tooltip to ")
            lbl.tooltip = tooltip

    def set_active(self, name: str, is_active: bool):
        self.query_one(f"#{name}_active", Label).update('🔴' if is_active else '🟢')
