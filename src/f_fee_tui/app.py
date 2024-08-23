from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Header, Footer
from textual.widgets import Label
from textual.widgets import Static
from textual.widgets import Switch


class FastFEEApp(App):
    """A Textual app to monitor and command the PLATO F-FEE."""

    CSS_PATH = "app.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield DEBMode()

    def on_mount(self) -> None:
        deb_mode_widget = self.query_one(DEBMode)
        deb_mode_widget.border_title = "DEB Mode"
        deb_mode_widget.border_subtitle = "What here?"

        # deb_mode_widget.styles.background = "blue"
        # deb_mode_widget.styles.color = "white"

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


class OnOffLed(Static):
    """A Label widget that represents a LED with two states: ON and OFF."""

    def __init__(self, state: bool) -> None:
        self.state = state
        super().__init__()

    def on_mount(self) -> None:
        # self.update("🟢" if self.state else "🔴")
        self.update("🟩" if self.state else "🟥")


class OnOffLedWithLabel(Widget):
    """A widget with a label and a LED with ON/OFF state."""

    def __init__(self, label: str, state: bool) -> None:
        self.label = label
        self.state = state
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.label)
        yield OnOffLed(self.state)
        # yield Switch(self.state)


class DEBMode(Static):
    """A widget to monitor the DEB mode."""

    def compose(self) -> ComposeResult:
        yield OnOffLedWithLabel("ON", True)
        yield OnOffLedWithLabel("STANDBY", False)
        yield OnOffLedWithLabel("FULL_IMAGE", False)
        yield OnOffLedWithLabel("FULL_IMAGE_PATTERN", False)
        yield OnOffLedWithLabel("WINDOWING", False)
        yield OnOffLedWithLabel("WINDOWING_PATTERN", False)
