from textual import events
from textual.app import ComposeResult
from textual.widgets import Button
from textual.widgets import Static

# Tooltips

BTN_SET_FPGA_DEFAULTS = """
Press this button to set the FPGA default values for the F-FEE DEB and AEB units. 

This command will take about 5 cycles: one cycle for settings the DEB defaults, and an additional cycle for each AEB unit.

"""

class GeneralCommand(Static):

    def compose(self) -> ComposeResult:
        yield Button("Set FPGA Defaults", id='btn-set-fpga-defaults', classes='command')

    def _on_mount(self, event: events.Mount) -> None:
        self.query_one("#btn-set-fpga-defaults").tooltip = BTN_SET_FPGA_DEFAULTS
