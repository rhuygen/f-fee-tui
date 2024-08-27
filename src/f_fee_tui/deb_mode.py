from textual.app import ComposeResult
from textual.widgets import Static

from .leds import OnOffLedWithLabel


class DEBMode(Static):
    """A widget to monitor the DEB mode."""

    def compose(self) -> ComposeResult:
        yield OnOffLedWithLabel("ON", True, id="deb-on")
        yield OnOffLedWithLabel("STANDBY", False, id="deb-standby")
        yield OnOffLedWithLabel("FULL_IMAGE", False, id="deb-full-image")
        yield OnOffLedWithLabel("FULL_IMAGE_PATTERN", False, id="deb-full-image-pattern")
        yield OnOffLedWithLabel("WINDOWING", False, id="deb-windowing")
        yield OnOffLedWithLabel("WINDOWING_PATTERN", False, id="deb-windowing-pattern")
