from textual.app import App
from textual.app import ComposeResult
from textual.widgets import Footer
from textual.widgets import Header

from f_fee_tui.deb_mode import DEBMode
from f_fee_tui.workers import DebModeChanged
from f_fee_tui.workers import ExceptionCaught
from f_fee_tui.workers import Monitor


class FastFEEApp(App):
    """A Textual app to monitor and command the PLATO F-FEE."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "to_standby", "Set DEB mode to STANDBY"),
    ]

    def __init__(self):
        super().__init__()
        self._monitoring_thread = Monitor(self)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield DEBMode()

    def on_mount(self) -> None:
        self._monitoring_thread.start()

        deb_mode_widget = self.query_one(DEBMode)
        deb_mode_widget.border_title = "DEB Mode"

    def on_unmount(self) -> None:
        self._monitoring_thread.cancel()
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join()

    def on_deb_mode_changed(self, message: DebModeChanged) -> None:
        mode = message.deb_mode

        self.query_one("#full_image").state = False
        self.query_one("#full_image_pattern").state = False
        self.query_one("#windowing").state = False
        self.query_one("#windowing_pattern").state = False
        self.query_one("#standby").state = False
        self.query_one("#on").state = False

        if mode == 0:
            self.query_one("#full_image").state = True
        elif mode == 1:
            self.query_one("#full_image_pattern").state = True
        elif mode == 2:
            self.query_one("#windowing").state = True
        elif mode == 3:
            self.query_one("#windowing_pattern").state = True
        elif mode == 6:
            self.query_one("#standby").state = True
        elif mode == 7:
            self.query_one("#on").state = True

    def on_exception_caught(self, message: ExceptionCaught):
        self.log(str(message.exc))
        self.log(str(message.tb))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_to_standby(self) -> None:
        self.query_one("#standby").state = True
        self.query_one("#on").state = False
