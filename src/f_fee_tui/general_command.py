from queue import Queue

from textual import events
from textual import on
from textual.app import ComposeResult
from textual.widgets import Button
from textual.widgets import Static

# Tooltips

BTN_SET_FPGA_DEFAULTS = """
Press this button to set the FPGA default values for the F-FEE DEB and AEB units. 

This command will take about 5 cycles: one cycle for settings the DEB defaults, and an additional cycle for each AEB unit.

"""

BTN_END_OBSERVATION = """
End the current observation.
"""


class GeneralCommand(Static):

    def __init__(self, command_q: Queue):
        super().__init__()
        self._command_q = command_q

    def compose(self) -> ComposeResult:
        yield Button("Set FPGA Defaults", id='btn-set-fpga-defaults', classes='command')
        yield Button("End observation", id="btn-end-observation", classes='command')

    def _on_mount(self, event: events.Mount) -> None:
        self.query_one("#btn-set-fpga-defaults").tooltip = BTN_SET_FPGA_DEFAULTS
        self.query_one("#btn-end-observation").tooltip = BTN_END_OBSERVATION

    @on(Button.Pressed, "#btn-end-observation")
    def command_end_observation(self):
        self.end_observation()

    def end_observation(self):

        self.notify("Ending the current observation")
        self._command_q.put_nowait(("CM_CS", "end_observation", [], {}))
