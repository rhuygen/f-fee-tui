from textual import events
from textual.app import ComposeResult
from textual.widgets import Button
from textual.widgets import Static

# Tooltips

BTN_DEB_ON = """
Press this button to bring the F-FEE in ON mode. 

ON mode can only be reached from STANDBY mode or FULL-IMAGE PATTERN mode.
"""
BTN_DEB_STANDBY = """
Press this button to bring the F-FEE in STANDBY mode.

STANDBY mode can only be reached from ON mode, and FULL-IMAGE mode.
"""
BTN_DEB_FULL_IMAGE = """
Press this button to bring the F-FEE into FULL-IMAGE mode.

FULL-IMAGE mode can only be reached from STANDBY mode.
"""
BTN_DEB_FULL_IMAGE_PATTERN = """
Press this button to bring the F-FEE into FULL-IMAGE PATTERN mode.

FULL-IMAGE PATTERN mode can only be reached from ON mode.
"""
BTN_DEB_IMMEDIATE_ON = """
Press this button to bring the F-FEE immediately into ON mode.

The DEB will return to ON mode immediately, regardless of the mode it is in. 
The AEBs will return to INIT state and power down the CCDs and the VASP.

Then, the AEBs will be Powered OFF.
"""

class DEBCommand(Static):

    HELP = """Press the button to change the DEB mode."""

    def compose(self) -> ComposeResult:
        yield Button("ON", id='btn-deb-on', classes='command')
        yield Button("FULL IMAGE PATTERN", id='btn-deb-full-image-pattern', classes='command')
        yield Button("STANDBY", id='btn-deb-standby', classes='command')
        yield Button("FULL IMAGE", id='btn-deb-full-image', classes='command')
        yield Button("IMMEDIATE ON", id='btn-deb-immediate-on', classes='command')

    def _on_mount(self, event: events.Mount) -> None:
        self.query_one("#btn-deb-on").tooltip = BTN_DEB_ON
        self.query_one("#btn-deb-standby").tooltip = BTN_DEB_STANDBY
        self.query_one("#btn-deb-full-image").tooltip = BTN_DEB_FULL_IMAGE
        self.query_one("#btn-deb-full-image-pattern").tooltip = BTN_DEB_FULL_IMAGE_PATTERN
        self.query_one("#btn-deb-immediate-on").tooltip = BTN_DEB_IMMEDIATE_ON
