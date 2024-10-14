import asyncio
import logging
import platform
import time
from typing import cast

import zmq
import zmq.asyncio
from egse.zmq import MessageIdentifier
from textual import on
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.command import Hit
from textual.command import Hits
from textual.command import Provider
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Sparkline

from ._queue import ClearableQueue
from .aeb_command import AEBCommand
from .aeb_state import AEBState
from .aeb_state import get_aeb_nr
from .deb_command import DEBCommand
from .deb_mode import DEBMode
from .dtc_in_mod import DtcInMod
from .general_command import GeneralCommand
from .infobar import InfoBar
from .messages import AebStateChanged
from .messages import CommandThreadCrashed
from .messages import DebModeChanged
from .messages import DtcInModChanged
from .messages import ExceptionCaught
from .messages import LogRetrieved
from .messages import OutbuffChanged
from .messages import ProblemDetected
from .messages import ShutdownReached
from .messages import TimeoutReached
from .services import handle_multi_part
from .services import handle_single_part
from .services import services
from .workers import Command
from .workers import Monitor

for handler in logging.getLogger().handlers:
    handler.setLevel(100)  # no logging levels to the screen


class ResetErrorsCommand(Provider):
    async def search(self, query: str) -> Hits:
        command = "Reset frame errors"
        matcher = self.matcher(query)
        score = matcher.match(command)

        self.app.log(f"{score = }")

        master_screen: MasterScreen = cast(MasterScreen, self.app.get_screen("master"))

        yield Hit(
            score,
            matcher.highlight(command),
            master_screen.reset_frame_errors,
            help="Clear the Sparkline that holds the accumulated frame errors.",
        )


class MasterScreen(Screen):

    BINDINGS = [
        Binding("ctrl+k", "toggle_commanding", "Toggle Commanding", show=False),
    ]

    COMMANDS = [ResetErrorsCommand]

    def __init__(self):
        super().__init__()
        self._command_q = ClearableQueue()
        self._monitoring_thread = Monitor(self.app)
        self._commanding_thread = Command(self.app, self._command_q)

        self._commanding_disabled = False
        self._commanding_widgets = []
        self._poll_timer = None

        self.title = "F-FEE TUI"
        self.sub_title = f"({platform.platform()})"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Vertical():
            with Horizontal():
                yield DEBMode(id="deb_modes")
                yield AEBState(id="aeb_states")
                yield DtcInMod(id="dtc_in_mod")
            with Horizontal():
                yield DEBCommand()
                yield AEBCommand()
                yield GeneralCommand(self._command_q)
            yield InfoBar(id="info-bar")

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

        self._commanding_widgets = [
            deb_command_widget, aeb_command_widget, general_command_widget
        ]
        self.action_toggle_commanding()

        self._poll_timer = self.set_timer(1.0, self.poll_services)

    def on_unmount(self) -> None:
        self._monitoring_thread.cancel()
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join()

        self._command_q.clear()
        self._command_q.join()

        self._commanding_thread.cancel()
        if self._commanding_thread.is_alive():
            self._commanding_thread.join()

    def reset_frame_errors(self):
        self._monitoring_thread.reset_frame_errors()

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
        self.query_one("GeneralCommand").disabled = True

        self.notify("Set FPGA defaults for the DEB")
        self._command_q.put_nowait(("DPU", "set_fpga_defaults", ['DEB'], {}))

        await asyncio.sleep(2.5)

        self.notify("Power ON all AEBs")
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
        self.query_one("GeneralCommand").disabled = False

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

    def on_outbuff_changed(self, message: OutbuffChanged):
        self.query_one("#frame-errors", Sparkline).data = message.outbuff
        self.query_one("#frame-errors", Sparkline).tooltip = str(message.outbuff)

    def on_aeb_state_changed(self, message: AebStateChanged):
        aeb_state: bool = message.aeb_state
        aeb_state_type: str = message.aeb_state_type

        aeb_state_widget = self.query_one(AEBState)
        aeb_state_widget.set_state(aeb_state_type, aeb_state)

        # Should only notify if new state != old state
        # self.notify(f"AEB State changed: {aeb_state_type}, {aeb_state}")

    def on_dtc_in_mod_changed(self, message: DtcInModChanged):
        dtc_in_mod_widget = self.query_one(DtcInMod)
        dtc_in_mod_widget.set_state(message)

    def on_log_retrieved(self, message: LogRetrieved):
        self.log(str(message.message))
        self.notify(message.message, title="Log INFO")

    def on_command_thread_crashed(self, message: CommandThreadCrashed):
        # The thread didn't really crash, but there was a communication error, so the Proxies' connect_cs() method
        # throws a ConnectionError. This exception is caught and after some sleep time the proxies try to reconnect.

        self.log.error(f"Command Thread Crashed: {message.exc}")

    def on_exception_caught(self, message: ExceptionCaught):
        self.log(str(message.exc))
        self.log(str(message.tb))

    def on_problem_detected(self, problem: ProblemDetected):
        self.notify(problem.message, severity="warning", title="WARNING")

    def on_timeout_reached(self, message: TimeoutReached):
        self.notify(message.message, title="Timeout")

    def on_shutdown_reached(self, message: ShutdownReached):
        self.notify(message.message, title="Shutdown")
        self.query_one("#deb_modes", DEBMode).clear()
        self.query_one("#aeb_states", AEBState).clear()
        self.query_one("#dtc_in_mod", DtcInMod).clear()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_toggle_commanding(self) -> None:
        self._commanding_disabled = not self._commanding_disabled

        for cmd_widget in self._commanding_widgets:
            cmd_widget.disabled = self._commanding_disabled

    @work()
    async def poll_services(self):

        ctx = zmq.asyncio.Context.instance()

        self.poller = zmq.asyncio.Poller()

        for name, props in services.items():
            sock = ctx.socket(props['type'])
            if props['type'] == zmq.SUB:
                sock.subscribe(props.get('subscribe', b''))
            sock.connect(f"tcp://{props['hostname']}:{props['port']}")

            props['sock'] = sock

            self.poller.register(sock, zmq.POLLIN)

        while True:
            events = dict(await self.poller.poll(timeout=100))

            current_time = time.monotonic()

            try:
                for name, props in services.items():
                    if (sock := props['sock']) in events and events[sock] == zmq.POLLIN:
                        message = await sock.recv()
                        more_parts = sock.getsockopt(zmq.RCVMORE)

                        if more_parts:
                            sync_id, response = await handle_multi_part(sock, message)
                        else:
                            sync_id, response = await handle_single_part(sock, message)

                        self.log.debug(f"Message received for {name} and {MessageIdentifier(sync_id).name}.")

                        props['callback'](self, name, sync_id, response, False)
                        self.query_one(InfoBar).set_active(name, False)
                        props['last_received'] = current_time
                        props['timed-out'] = False
                    else:
                        if not props['timed-out'] and current_time - props['last_received'] > props['interval']:
                            self.log(f"No message received for {name} within {props['interval']}.")
                            props['timed-out'] = True
                            props['callback'](self, name, None, None, True)
                            self.query_one(InfoBar).set_active(name, True)
            except NoMatches as exc:
                pass

            # Sleep for a while before polling again
            await asyncio.sleep(1.0)
