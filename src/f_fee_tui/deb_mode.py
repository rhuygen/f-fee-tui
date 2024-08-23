from textual.app import ComposeResult
from textual.widgets import Static

from f_fee_tui.leds import OnOffLedWithLabel


class DEBMode(Static):
    """A widget to monitor the DEB mode."""

    def compose(self) -> ComposeResult:
        yield OnOffLedWithLabel("ON", True, id="on")
        yield OnOffLedWithLabel("STANDBY", False, id="standby")
        yield OnOffLedWithLabel("FULL_IMAGE", False)
        yield OnOffLedWithLabel("FULL_IMAGE_PATTERN", False)
        yield OnOffLedWithLabel("WINDOWING", False)
        yield OnOffLedWithLabel("WINDOWING_PATTERN", False)
