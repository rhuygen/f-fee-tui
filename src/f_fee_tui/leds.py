from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label
from textual.widgets import Static


class OnOffLed(Static):
    """A Label widget that represents a LED with two states: ON and OFF."""

    state = reactive(False)

    def watch_state(self, state: bool) -> None:
        # self.update("🟢" if self.state else "🔴")
        self.update("🟩" if state else "🟥")


class OnOffLedWithLabel(Widget):
    """A widget with a label and a LED with ON/OFF state."""

    def __init__(self, label: str, state: bool, id: str = None) -> None:
        self.label = label
        self._state = state
        super().__init__(id=id)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: bool):
        self._state = state
        self.led.state = state

    def compose(self) -> ComposeResult:
        self.led = OnOffLed()
        self.led.state = self.state

        yield Label(self.label)
        yield self.led
