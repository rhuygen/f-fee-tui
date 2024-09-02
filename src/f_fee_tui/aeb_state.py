import re

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

    def set_state(self, aeb_state_type: str, aeb_state: bool):

        if (aeb_nr := get_aeb_nr(aeb_state_type)) is None:
            self.notify(f"Couldn't derive AEB unit number from {aeb_state_type=}", severity="warning")
            return

        if aeb_state_type.endswith("onoff"):
            self.query_one(f"#{aeb_state_type}", OnOffLed).state = bool(aeb_state)
        else:
            # Clear the previous state

            self.query_one(f"#aeb{aeb_nr}_init", OnOffLed).state = False
            self.query_one(f"#aeb{aeb_nr}_config", OnOffLed).state = False
            self.query_one(f"#aeb{aeb_nr}_image", OnOffLed).state = False
            self.query_one(f"#aeb{aeb_nr}_pattern", OnOffLed).state = False

            self.query_one(f"#{aeb_state_type}", OnOffLed).state = aeb_state


def get_aeb_nr(string: str):

    # The first digit that is matched in 'string' will be returned.
    #
    # This is used for:
    # - button.id -> 'btn-aeb[1-4]-[\w-]+'
    # -

    match = re.search(r'\d', string)
    if match:
        aeb_nr = int(match.group())
    else:
        aeb_nr = None

    return aeb_nr
