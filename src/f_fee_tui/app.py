import re
from queue import Queue

from textual import on
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header

from .aeb_command import AEBCommand
from .aeb_state import AEBState
from .deb_command import DEBCommand
from .deb_mode import DEBMode
from .messages import AebStateChanged
from .messages import DebModeChanged
from .messages import ExceptionCaught
from .messages import ProblemDetected
from .messages import TimeoutReached
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
            yield AEBState()
        with Horizontal():
            yield DEBCommand()
            yield AEBCommand()

    def on_mount(self) -> None:
        self._monitoring_thread.start()
        self._commanding_thread.start()

        deb_mode_widget = self.query_one(DEBMode)
        deb_mode_widget.border_title = "DEB Mode"

        deb_command_widget = self.query_one(DEBCommand)
        deb_command_widget.border_title = "DEB Commanding"

        aeb_state_widget = self.query_one(AEBState)
        aeb_state_widget.border_title = "AEB State"

        aeb_command_widget = self.query_one(AEBCommand)
        aeb_command_widget.border_title = "AEB Commanding"


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

    @on(Button.Pressed, ".command.aeb.power")
    def command_aeb_power(self, message: Button.Pressed):
        button = message.button

        # Determine if power-on or power-off was requested
        cmd = "deb_set_aeb_power_on" if button.id.endswith("-on") else "deb_set_aeb_power_off"

        # button.id shall have the following format 'btn-aeb[1-4]-[\w-]+'
        match = re.search(r'\d', button.id)
        if match:
            aeb_nr = int(match.group())
        else:
            self.notify(message=f"Couldn't match AEB number in {button.id}", severity="error", timeout=5.0)
            return

        args = [1 if aeb_nr == x else 0 for x in (1, 2, 3, 4)]

        self._command_q.put_nowait(("DPU", cmd, args, {}))

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

    def on_aeb_state_changed(self, message: AebStateChanged):
        aeb_state = message.aeb_state
        aeb_state_type = message.aeb_state_type

        aeb_state_widget = self.query_one(AEBState)
        aeb_state_widget.set_state(aeb_state_type, aeb_state)

        self.notify(f"AEB State changed: {aeb_state_type}, {aeb_state}")

    def on_exception_caught(self, message: ExceptionCaught):
        self.log(str(message.exc))
        self.log(str(message.tb))

    def on_problem_detected(self, problem: ProblemDetected):
        self.notify(problem.message, severity="warning", title="WARNING")

    def on_timeout_reached(self, message: TimeoutReached):
        self.notify(message.message, title="Timeout")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
