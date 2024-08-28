from textual.app import ComposeResult
from textual.widgets import Label
from textual.widgets import Static

from .leds import OnOffLed


class AEBState(Static):
    """A widget to monitor the state of the AEBs."""

    def compose(self) -> ComposeResult:
        yield Label()
        yield Label("ON/OFF", classes="title")
        yield Label("INIT", classes="title")
        yield Label("CONFIG", classes="title")
        yield Label("IMAGE", classes="title")
        yield Label("PATTERN", classes="title")

        yield Label("AEB1")
        yield OnOffLed(id="aeb1_onoff")
        yield OnOffLed(id="aeb1_init")
        yield OnOffLed(id="aeb1_config")
        yield OnOffLed(id="aeb1_image")
        yield OnOffLed(id="aeb1_pattern")

        yield Label("AEB2")
        yield OnOffLed(id="aeb2_onoff")
        yield OnOffLed(id="aeb2_init")
        yield OnOffLed(id="aeb2_config")
        yield OnOffLed(id="aeb2_image")
        yield OnOffLed(id="aeb2_pattern")

        yield Label("AEB3")
        yield OnOffLed(id="aeb3_onoff")
        yield OnOffLed(id="aeb3_init")
        yield OnOffLed(id="aeb3_config")
        yield OnOffLed(id="aeb3_image")
        yield OnOffLed(id="aeb3_pattern")

        yield Label("AEB4")
        yield OnOffLed(id="aeb4_onoff")
        yield OnOffLed(id="aeb4_init")
        yield OnOffLed(id="aeb4_config")
        yield OnOffLed(id="aeb4_image")
        yield OnOffLed(id="aeb4_pattern")

    def set_state(self, aeb_state_type, aeb_state):
        self.query_one(f"#{aeb_state_type}", OnOffLed).state = bool(aeb_state)
