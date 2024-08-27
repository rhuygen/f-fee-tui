from queue import Queue

from textual import on
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header

from .deb_command import DEBCommand
from .deb_mode import DEBMode
from .messages import DebModeChanged
from .messages import ExceptionCaught
from .workers import Command
from .workers import Monitor


class FastFEEApp(App):
    """A Textual app to monitor and command the PLATO F-FEE."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self):
        super().__init__()
        self._command_q = Queue()
        self._monitoring_thread = Monitor(self)
        self._commanding_thread = Command(self, self._command_q)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Horizontal():
            yield DEBMode()
            yield DEBCommand()

    def on_mount(self) -> None:
        self._monitoring_thread.start()
        self._commanding_thread.start()

        deb_mode_widget = self.query_one(DEBMode)
        deb_mode_widget.border_title = "DEB Mode"

        deb_command_widget = self.query_one(DEBCommand)
        deb_command_widget.border_title = "DEB Commanding"

    def on_unmount(self) -> None:
        self._monitoring_thread.cancel()
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join()

        self._command_q.join()

        self._commanding_thread.cancel()
        if self._commanding_thread.is_alive():
            self._commanding_thread.join()

    @on(Button.Pressed, "#btn-deb-on")
    def command_deb_to_on_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_on_mode", [], {}))

    @on(Button.Pressed, "#btn-deb-immediate-on")
    def command_deb_to_immediate_on(self):
        self._command_q.put_nowait(("DPU", "deb_set_immediate_on", [], {}))

    @on(Button.Pressed, "#btn-deb-standby")
    def command_deb_to_standby_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_standby_mode", [], {}))

    @on(Button.Pressed, "#btn-deb-full-image")
    def command_deb_to_full_image_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_full_image_mode", [], {}))

    @on(Button.Pressed, "#btn-deb-full-image-pattern")
    def command_deb_to_full_image_pattern_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_full_image_pattern_mode", [], {}))

    def on_deb_mode_changed(self, message: DebModeChanged) -> None:
        mode = message.deb_mode

        self.query_one("#deb-full-image").state = False
        self.query_one("#deb-full-image-pattern").state = False
        self.query_one("#deb-windowing").state = False
        self.query_one("#deb-windowing-pattern").state = False
        self.query_one("#deb-standby").state = False
        self.query_one("#deb-on").state = False

        if mode == 0:
            self.query_one("#deb-full-image").state = True
        elif mode == 1:
            self.query_one("#deb-full-image-pattern").state = True
        elif mode == 2:
            self.query_one("#deb-windowing").state = True
        elif mode == 3:
            self.query_one("#deb-windowing-pattern").state = True
        elif mode == 6:
            self.query_one("#deb-standby").state = True
        elif mode == 7:
            self.query_one("#deb-on").state = True

        from egse.fee.ffee import f_fee_mode
        self.notify(f"F-FEE set to {f_fee_mode(mode).name}")

    def on_exception_caught(self, message: ExceptionCaught):
        self.log(str(message.exc))
        self.log(str(message.tb))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
