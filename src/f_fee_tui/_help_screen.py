"""The main help dialog for the application."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center
from textual.containers import Vertical
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Markdown

from f_fee_tui._version import get_version

HERE = Path(__file__).parent

HELP: Final[
    str
] = f"""
# F-FEE Commanding and Monitoring Tool [v{get_version()}]

Welcome to F-FEE-TUI Help!

"""


class HelpScreen(ModalScreen[None]):
    """Modal dialog that shows the application's help."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Vertical {
        border: thick $primary 50%;
        width: 60%;
        height: 80%;
        background: $boost;
    }

    HelpScreen > Vertical > VerticalScroll {
        height: 1fr;
    }

    HelpScreen > Vertical > Center {
        padding: 1;
        height: auto;
    }
    """

    BINDINGS = [Binding("escape", "app.pop_screen", "", show=False)]

    def compose(self) -> ComposeResult:
        with open(f"{HERE / 'help.md'}", encoding="utf-8") as f:
            help_text = f.read()
        with Vertical():
            with VerticalScroll():
                yield Markdown(HELP + help_text)
            with Center():
                yield Button("Close", variant="primary")

    def on_mount(self) -> None:
        # It seems that some things inside Markdown can still grab focus;
        # which might not be right. Let's ensure that can't happen here.
        self.query_one(Markdown).can_focus_children = False
        self.query_one("Vertical > VerticalScroll").focus()

    def on_button_pressed(self) -> None:
        """React to button press."""
        self.dismiss(None)

    def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        """A link was clicked in the help."""
        self.app.open_url(event.href)
