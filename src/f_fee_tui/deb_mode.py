from textual.app import ComposeResult
from textual.widgets import Static

from f_fee_tui.leds import OnOffLedWithLabel


class DEBMode(Static):
    """A widget to monitor the DEB mode."""

    def compose(self) -> ComposeResult:
        yield OnOffLedWithLabel("ON", True, id="on")
        yield OnOffLedWithLabel("STANDBY", False, id="standby")
        yield OnOffLedWithLabel("FULL_IMAGE", False, id="full_image")
        yield OnOffLedWithLabel("FULL_IMAGE_PATTERN", False, id="full_image_pattern")
        yield OnOffLedWithLabel("WINDOWING", False, id="windowing")
        yield OnOffLedWithLabel("WINDOWING_PATTERN", False, id="windowing_pattern")
