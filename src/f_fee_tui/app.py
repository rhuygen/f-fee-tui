import asyncio
import platform
from queue import Queue

from textual import on
from textual import work
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header

from .aeb_command import AEBCommand
from .aeb_state import AEBState
from .aeb_state import get_aeb_nr
from .deb_command import DEBCommand
from .deb_mode import DEBMode
from .dtc_in_mod import DtcInMod
from .general_command import GeneralCommand
from .messages import AebStateChanged
from .messages import DebModeChanged
from .messages import DtcInModChanged
from .messages import ExceptionCaught
from .messages import ProblemDetected
from .messages import TimeoutReached
from .workers import Command
from .workers import Monitor


class FastFEEApp(App):
    """A Textual app to monitor and command the PLATO F-FEE."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self):
        super().__init__()
        self._command_q = Queue()
        self._monitoring_thread = Monitor(self)
        self._commanding_thread = Command(self, self._command_q)

        self.title = "F-FEE TUI"
        self.sub_title = f"({platform.platform()})"


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Horizontal():
            yield DEBMode()
            yield AEBState()
            yield DtcInMod()
        with Horizontal():
            yield DEBCommand()
            yield AEBCommand()
            yield GeneralCommand()

    def on_mount(self) -> None:
        self._monitoring_thread.start()
        self._commanding_thread.start()

        deb_mode_widget = self.query_one(DEBMode)
        deb_mode_widget.border_title = "DEB Mode"

        deb_command_widget = self.query_one(DEBCommand)
        deb_command_widget.border_title = "DEB Commanding"

        aeb_state_widget = self.query_one(AEBState)
        aeb_state_widget.border_title = "AEB State"

        in_mod_widget = self.query_one(DtcInMod)
        in_mod_widget.border_title = "DTC IN_MOD"

        aeb_command_widget = self.query_one(AEBCommand)
        aeb_command_widget.border_title = "AEB Commanding"

        general_command_widget = self.query_one(GeneralCommand)
        general_command_widget.border_title = "General Commanding"


    def on_unmount(self) -> None:
        self._monitoring_thread.cancel()
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join()

        self._command_q.join()  # FIXME: this blocks when the DPU CS is not responding or not running

        self._commanding_thread.cancel()
        if self._commanding_thread.is_alive():
            self._commanding_thread.join()

    @on(Button.Pressed, "#btn-deb-on")
    def command_deb_to_on_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_on_mode", [], {}))

    @on(Button.Pressed, "#btn-deb-immediate-on")
    async def command_deb_to_immediate_on(self):
        self._command_q.put_nowait(("DPU", "deb_set_immediate_on", [], {}))
        for aeb_id in "AEB1", "AEB2", "AEB3", "AEB4":
            self._command_q.put_nowait(("DPU", "aeb_set_init_mode", [aeb_id], {}))
        await asyncio.sleep(6.0)
        self._command_q.put_nowait(("DPU", "deb_set_aeb_power_off", [True, True, True, True], {}))

    @on(Button.Pressed, "#btn-deb-standby")
    def command_deb_to_standby_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_standby_mode", [], {}))

    @on(Button.Pressed, "#btn-deb-full-image")
    def command_deb_to_full_image_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_full_image_mode", [], {}))

    @on(Button.Pressed, "#btn-deb-full-image-pattern")
    def command_deb_to_full_image_pattern_mode(self):
        self._command_q.put_nowait(("DPU", "deb_set_full_image_pattern_mode", [], {}))

    @on(Button.Pressed, "#btn-set-fpga-defaults")
    async def command_set_fpga_defaults(self):
        self.set_fpga_defaults()

    @work()
    async def set_fpga_defaults(self):
        self.query_one("DEBCommand").disabled = True
        self.query_one("AEBCommand").disabled = True

        self.notify("Set FPGA defaults for the DEB")
        self._command_q.put_nowait(("DPU", "set_fpga_defaults", ['DEB'], {}))

        await asyncio.sleep(2.5)

        power_on_sequence = [False, False, False, False]
        for idx, aeb_id in enumerate(('AEB1', 'AEB2', 'AEB3', 'AEB4')):
            power_on_sequence[idx] = True
            self._command_q.put_nowait(("DPU", "deb_set_aeb_power_on", power_on_sequence, {}))

            await asyncio.sleep(2.5)

        for unit in 'AEB1', 'AEB2', 'AEB3', 'AEB4':
            self.notify(f"Set FPGA defaults for the {unit}")
            self._command_q.put_nowait(("DPU", "set_fpga_defaults", [unit], {}))

        self.query_one("DEBCommand").disabled = False
        self.query_one("AEBCommand").disabled = False

    @on(Button.Pressed, ".command.aeb.power")
    def command_aeb_power(self, message: Button.Pressed):
        button = message.button

        # Determine if power-on or power-off was requested
        cmd = "deb_set_aeb_power_on" if button.id.endswith("-on") else "deb_set_aeb_power_off"

        if (aeb_nr := get_aeb_nr(button.id)) is None:
            self.notify(message=f"Couldn't match AEB number in {button.id}", severity="error", timeout=5.0)
            return

        args = [1 if aeb_nr == x else 0 for x in (1, 2, 3, 4)]

        self._command_q.put_nowait(("DPU", cmd, args, {}))

    @on(Button.Pressed, ".command.aeb.init")
    def command_aeb_to_init(self, message: Button.Pressed):
        button = message.button

        cmd = "aeb_set_init_mode"

        if (aeb_nr := get_aeb_nr(button.id)) is None:
            self.notify(message=f"Couldn't match AEB number in {button.id}", severity="error", timeout=5.0)
            return

        args = [f"AEB{aeb_nr}"]

        self._command_q.put_nowait(("DPU", cmd, args, {}))

    @on(Button.Pressed, ".command.aeb.config")
    def command_aeb_to_config(self, message: Button.Pressed):
        button = message.button

        cmd = "aeb_set_config_mode"

        if (aeb_nr := get_aeb_nr(button.id)) is None:
            self.notify(message=f"Couldn't match AEB number in {button.id}", severity="error", timeout=5.0)
            return

        args = [f"AEB{aeb_nr}"]

        self._command_q.put_nowait(("DPU", cmd, args, {}))

    @on(Button.Pressed, ".command.aeb.image")
    def command_aeb_to_image(self, message: Button.Pressed):
        button = message.button

        cmd = "aeb_set_image_mode"

        if (aeb_nr := get_aeb_nr(button.id)) is None:
            self.notify(message=f"Couldn't match AEB number in {button.id}", severity="error", timeout=5.0)
            return

        args = [f"AEB{aeb_nr}"]

        self._command_q.put_nowait(("DPU", cmd, args, {}))

    @on(Button.Pressed, ".command.aeb.pattern")
    def command_aeb_to_pattern(self, message: Button.Pressed):
        button = message.button

        self.notify("AEB Pattern mode not yet implemented.", severity="warning")

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

        # Should only notify if new state != old state
        # from egse.fee.ffee import f_fee_mode
        # self.notify(f"F-FEE set to {f_fee_mode(mode).name}")

    def on_aeb_state_changed(self, message: AebStateChanged):
        aeb_state: bool = message.aeb_state
        aeb_state_type: str = message.aeb_state_type

        aeb_state_widget = self.query_one(AEBState)
        aeb_state_widget.set_state(aeb_state_type, aeb_state)

        # Should only notify if new state != old state
        # self.notify(f"AEB State changed: {aeb_state_type}, {aeb_state}")

    def on_dtc_in_mod_state_changed(self, message: DtcInModChanged):
        dtc_in_mod_state_widget = self.query_one(DtcInMod)
        dtc_in_mod_state_widget.set_state(message)

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
