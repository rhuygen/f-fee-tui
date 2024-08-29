import re

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Label
from textual.widgets import Static
from textual.widgets import TabPane
from textual.widgets import TabbedContent


# Tooltips
BTN_AEB_POWER_ON = """
AEB-{} Power ON

This will switch ON the AEB unit and bring it into INIT mode. CCDs and VASP are not powered. No HK is sent.
"""
BTN_AEB_POWER_OFF = """
AEB-{} Power OFF

This will Switch OFF the AEB unit.
"""


class AEBCommand(Static):

    HELP = """Press the button to change the AEB mode."""

    def compose(self) -> ComposeResult:
        with TabbedContent():
            for aeb_nr in 1, 2, 3, 4:
                with TabPane(f"AEB{aeb_nr}"):
                    with Horizontal():
                        yield Label("POWER")
                        yield Button("ON", id=f'btn-aeb{aeb_nr}-on', classes='command aeb power')
                        yield Button("OFF", id=f'btn-aeb{aeb_nr}-off', classes='command aeb power')
                    with Horizontal():
                        yield Label("MODE")
                        yield Button("INIT", id=f'btn-aeb{aeb_nr}-init', classes='command aeb init')
                        yield Button("CONFIG", id=f'btn-aeb{aeb_nr}-config', classes='command aeb config')
                        yield Button("IMAGE", id=f'btn-aeb{aeb_nr}-image', classes='command aeb image')
                        yield Button("PATTERN", id=f'btn-aeb{aeb_nr}-pattern', classes='command aeb pattern')

    def _on_mount(self, event: events.Mount) -> None:
        for widget in self.query(".power").results(Button):
            aeb_nr = extract_aeb_nr(widget)
            if widget.id.endswith("-on"):
                widget.tooltip = BTN_AEB_POWER_ON.format(aeb_nr)
            else:
                widget.tooltip = BTN_AEB_POWER_OFF.format(aeb_nr)


def extract_aeb_nr(button):
    """Extract the AEB number 1,2,3,4 from the button's identifier. Zero (0) is returned when the match failed."""
    # button.id shall have the following format 'btn-aeb[1-4]-[\w-]+'
    match = re.search(r'\d', button.id)
    if match:
        aeb_nr = int(match.group())
    else:
        aeb_nr = 0

    return aeb_nr
