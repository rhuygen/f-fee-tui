from __future__ import annotations

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Markdown
from textual.widgets import Select


class InputStringDialog(ModalScreen[Optional[str]]):
    """A modal dialog asking for an input string."""

    BINDINGS = [Binding("escape", "dismiss(False)", "", show=False)]

    def __init__(self, default_input: str, title: str = None):
        super().__init__()

        self._title = title or "Question"
        self._default_input = default_input
        self._description = default_input

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title)
            yield Input(placeholder=self._default_input)
            with Horizontal():
                yield Button("OK", variant="primary", id="btn-dialog-ok")
                yield Button("Cancel", id="btn-dialog-cancel")

    @on(Input.Changed)
    def save_description(self, event: Input.Changed) -> None:
        self._description = event.value

    @on(Input.Submitted)
    def return_pressed(self, event: Input.Submitted):
        self._description = event.value

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """React to button press."""

        if event.button.id == "btn-dialog-ok":
            self.dismiss(self._description or self._default_input)
            # self.app.query_one("#console-log", ConsoleOutput).write_log_info("You pressed YES...")
        else:
            self.dismiss(None)
            # self.app.query_one("#console-log", ConsoleOutput).write_log_info("You pressed NO...")


class YesNoDialog(ModalScreen[bool]):
    """A modal dialog that asks a YES / NO question."""

    BINDINGS = [Binding("escape", "dismiss(False)", "", show=False)]

    def __init__(self, question: str, title: str = None):
        super().__init__()

        self._title = title or "Question"
        self._question = question

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title)
            yield Markdown(self._question)
            with Horizontal():
                yield Button("Yes", variant="primary", id="btn-dialog-yes")
                yield Button("No", id="btn-dialog-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """React to button press."""

        if event.button.id == "btn-dialog-yes":
            self.dismiss(True)
            # self.app.query_one("#console-log", ConsoleOutput).write_log_info("You pressed YES...")
        else:
            self.dismiss(False)
            # self.app.query_one("#console-log", ConsoleOutput).write_log_info("You pressed NO...")


class SelectDialog(ModalScreen[int]):
    """A modal dialog with a selection from which to choose."""

    BINDINGS = [Binding("escape", "dismiss(-1)", "", show=False)]

    def __init__(self, options: list[str], title: str = None, message: str = None, footer: str = None):
        super().__init__()

        self._title = title or "Select one of the options"
        self._message = message or ""
        self._options = [(str(y), x) for x, y in enumerate(options)]
        self._footer = footer or "Press [i]escape[/] to dismiss this dialog."
        self._selected_index = -1

    def compose(self) -> ComposeResult:

        with Vertical():
            yield Label(self._title)
            yield Markdown(self._message)
            yield Select(self._options)
            with Horizontal():
                yield Button("OK", variant="primary", id="btn-dialog-ok")
                yield Button("Cancel", id="btn-dialog-cancel")
            if self._footer:
                yield Label(self._footer, id="lbl-dialog-footer")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self._selected_index = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """React to button press."""

        if event.button.id == "btn-dialog-ok":
            self.dismiss(self._selected_index)
        else:
            self.dismiss(-1)
