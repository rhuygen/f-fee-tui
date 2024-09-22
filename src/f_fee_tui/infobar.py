from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label

from f_fee_tui.services import services


class InfoBar(Horizontal):

    DEFAULT_CSS = """
    InfoBar {
        height: 1;
        dock: bottom;
        Label {
            margin: 0 1 0 0; 
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("cm_cs", id="cm_cs")
        yield Label("🔴", id="cm_cs_active", classes="status")
        yield Label("sm_cs", id="sm_cs")
        yield Label("🔴", id="sm_cs_active", classes="status")
        yield Label("pm_cs", id="pm_cs")
        yield Label("🔴", id="pm_cs_active", classes="status")
        yield Label("syn_cs", id="syn_cs")
        yield Label("🔴", id="syn_cs_active", classes="status")
        yield Label("dump", id="data_dump")
        yield Label("🔴", id="data_dump_active", classes="status")
        yield Label("dpu_cs", id="dpu_cs")
        yield Label("🔴", id="dpu_cs_active", classes="status")
        yield Label("data", id="data")
        yield Label("🔴", id="data_active", classes="status")

    def on_mount(self, event: events.Mount) -> None:

        for name, props in services.items():
            lbl = self.query_one(f"#{name}", Label)
            tooltip = props.get('description', '')
            self.app.log(f"Added tooltip to ")
            lbl.tooltip = tooltip

    def set_active(self, name: str, is_active: bool):
        self.query_one(f"#{name}_active", Label).update('🔴' if is_active else '🟢')
