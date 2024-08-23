from textual.app import App
from textual.app import ComposeResult
from textual.widgets import Footer
from textual.widgets import Header

from f_fee_tui.deb_mode import DEBMode


class FastFEEApp(App):
    """A Textual app to monitor and command the PLATO F-FEE."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "to_standby", "Set DEB mode to STANDBY"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield DEBMode()

    def on_mount(self) -> None:
        deb_mode_widget = self.query_one(DEBMode)
        deb_mode_widget.border_title = "DEB Mode"

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_to_standby(self) -> None:
        self.query_one("#standby").state = True
        self.query_one("#on").state = False
