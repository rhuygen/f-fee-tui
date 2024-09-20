import itertools

from textual.app import ComposeResult
from textual.widgets import Label
from textual.widgets import Static

from f_fee_tui.messages import DtcInModChanged

ON = "✖"
OFF = ""

T0 = {0b001: "T0-001"}
T1 = {0b001: "T1-001", 0b010: "T1-010"}
T2 = {0b001: "T2-001", 0b010: "T2-010"}
T3 = {0b001: "T3-001"}
T4 = {0b001: "T4-001"}
T5 = {0b001: "T5-001", 0b010: "T5-010"}
T6 = {0b001: "T6-001", 0b010: "T6-010"}
T7 = {0b001: "T7-001"}

ALL_IDS = list(itertools.chain(
        T0.values(), T1.values(), T2.values(), T3.values(), T4.values(), T5.values(), T6.values(), T7.values()
))


class DtcInMod(Static):
    """A widget to monitor the state of the AEBs."""

    def compose(self) -> ComposeResult:
        yield Label("", classes="header")
        yield Label("AEB1", classes="two-cols header")
        yield Label("AEB2", classes="two-cols header")
        yield Label("AEB3", classes="two-cols header")
        yield Label("AEB4", classes="two-cols header")

        yield Label("SpW 1")
        yield Label("", id="T1-001", classes="one-col")    # AEB1-E
        yield Label("", id="T0-001", classes="one-col")    # AEB1-F
        yield Label("", classes="one-col disabled")
        yield Label("", id="T1-010", classes="one-col")    # AEB2-F
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")

        yield Label("SpW 2")
        yield Label("", id="T2-010", classes="one-col")    # AEB1-E
        yield Label("", classes="one-col disabled")
        yield Label("", id="T3-001", classes="one-col")    # AEB2-E
        yield Label("", id="T2-001", classes="one-col")    # AEB2-F
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")

        yield Label("SpW 3")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", id="T5-001", classes="one-col")    # AEB3-E
        yield Label("", id="T4-001", classes="one-col")    # AEB3-F
        yield Label("", classes="one-col disabled")
        yield Label("", id="T5-010", classes="one-col")    # AEB4-F

        yield Label("SpW 4")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", classes="one-col disabled")
        yield Label("", id="T6-010", classes="one-col")    # AEB3-E
        yield Label("", classes="one-col disabled")
        yield Label("", id="T7-001", classes="one-col")    # AEB4-E
        yield Label("", id="T6-001", classes="one-col")    # AEB4-F

        yield Label("")
        yield Label("E", classes="one-col footer")
        yield Label("F", classes="one-col footer")
        yield Label("E", classes="one-col footer")
        yield Label("F", classes="one-col footer")
        yield Label("E", classes="one-col footer")
        yield Label("F", classes="one-col footer")
        yield Label("E", classes="one-col footer")
        yield Label("F", classes="one-col footer")

    def set_state(self, state: DtcInModChanged):
        self.log(f"{state.t0=}, {state.t1=}, {state.t2=}, {state.t3=}, {state.t4=}, {state.t5=}, {state.t6=}, {state.t7=}")
        for id_ in ALL_IDS:
            self.query_one(f"#{id_}", Label).update(OFF)

        if state.t0 == 0b001:
            self.query_one("#T0-001", Label).update(ON)

        if state.t1 == 0b001:
            self.query_one("#T1-001", Label).update(ON)
        elif state.t1 == 0b010:
            self.query_one("#T1-010", Label).update(ON)

        if state.t2 == 0b001:
            self.query_one("#T2-001", Label).update(ON)
        elif state.t2 == 0b010:
            self.query_one("#T2-010", Label).update(ON)

        if state.t3 == 0b001:
            self.query_one("#T3-001", Label).update(ON)

        if state.t4 == 0b001:
            self.query_one("#T4-001", Label).update(ON)

        if state.t5 == 0b001:
            self.query_one("#T5-001", Label).update(ON)
        elif state.t5 == 0b010:
            self.query_one("#T5-010", Label).update(ON)

        if state.t6 == 0b001:
            self.query_one("#T6-001", Label).update(ON)
        elif state.t6 == 0b010:
            self.query_one("#T6-010", Label).update(ON)

        if state.t7 == 0b001:
            self.query_one("#T7-001", Label).update(ON)
