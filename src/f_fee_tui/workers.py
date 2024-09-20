from __future__ import annotations

import logging
import pickle
import queue
import threading
import time
import traceback
from queue import Queue
from typing import TYPE_CHECKING

import zmq
from egse.dpu.fdpu import FastCameraDPUProxy
from egse.fee.ffee import HousekeepingData
from egse.fee.ffee import aeb_state
from egse.fee.ffee import f_fee_mode
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.setup import load_setup
from egse.zmq import MessageIdentifier

from .messages import AebStateChanged
from .messages import DebModeChanged
from .messages import DtcInModChanged
from .messages import ExceptionCaught
from .messages import TimeoutReached

if TYPE_CHECKING:
    from .app import FastFEEApp

_LOGGER = logging.getLogger("egse.f-fee-tui")

dpu = Settings.load("DPU Processor")


class Command(threading.Thread):
    def __init__(self, app: 'FastFEEApp', command_q: Queue) -> None:
        super().__init__()
        self._app = app
        self._command_q = command_q
        self._f_dpu: FastCameraDPUProxy | None = None
        self._canceled = threading.Event()

    def run(self) -> None:

        with FastCameraDPUProxy() as self._f_dpu:
            while True:
                if self._canceled.is_set():
                    break
                try:
                    target, command, args, kwargs = self._command_q.get_nowait()
                    self.execute_command(target, command, args, kwargs)
                    self._command_q.task_done()
                except queue.Empty:
                    time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
                    continue
                except Exception as exc:
                    _LOGGER.error(f"Caught and exception: {exc}")
                    tb = traceback.format_exc()
                    self._app.post_message(ExceptionCaught(exc, tb))

    def cancel(self) -> None:
        self._canceled.set()

    def execute_command(self, target: str, command: str, args: list, kwargs: dict):
        if target == "DPU":
            try:
                return getattr(self._f_dpu, command)(*args, **kwargs)
            except AttributeError as exc:
                _LOGGER.error(f"No such command for DPU: {command}", exc_info=True)


class Monitor(threading.Thread):
    def __init__(self, app: 'FastFEEApp') -> None:
        self._app = app
        self._canceled = threading.Event()
        self.hostname = dpu.HOSTNAME
        self.port = dpu.DATA_DISTRIBUTION_PORT

        self.previous_deb_mode = f_fee_mode.ON_MODE
        self.previous_aeb_state = {}

        super().__init__()

    def run(self) -> None:

        n_timeouts = 0
        """The timeout is 1s, we count the number of timeouts to detect if the DPU or N-FEE might be dead or stalled."""

        context = zmq.Context.instance()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt_string(zmq.SUBSCRIBE, "")
        receiver.connect(f"tcp://{self.hostname}:{self.port}")

        setup = load_setup()

        while True:
            if self._canceled.is_set():
                break

            socket_list, _, _ = zmq.select([receiver], [], [], timeout=1.0)

            if receiver in socket_list:
                n_timeouts = 0
                try:
                    sync_id, pickle_string = receiver.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                    data = pickle.loads(pickle_string)
                    self.handle_messages(sync_id, data, setup)
                except Exception as exc:
                    tb = traceback.format_exc()
                    self._app.post_message(ExceptionCaught(exc, tb))

            if len(socket_list) == 0:
                n_timeouts += 1
                if n_timeouts > 3:  # at least a timecode should arrive every 2.5s
                    self._app.post_message(TimeoutReached("Timeout reached after 3s on monitoring channel."))
                    n_timeouts = 0

        receiver.disconnect(f"tcp://{self.hostname}:{self.port}")
        receiver.close()

    def cancel(self) -> None:
        self._canceled.set()

    def handle_messages(self, sync_id, data, setup):

        if sync_id == MessageIdentifier.F_FEE_REGISTER_MAP:

            # How can we be sure the Register Map is properly synchronised with the F-FEE?

            register_map, _ = data
            register_map = RegisterMap("F-FEE", memory_map=register_map, setup=setup)

            t0 = register_map["DEB_DTC_IN_MOD_2", "T0_IN_MOD"]
            t1 = register_map["DEB_DTC_IN_MOD_2", "T1_IN_MOD"]
            t2 = register_map["DEB_DTC_IN_MOD_2", "T2_IN_MOD"]
            t3 = register_map["DEB_DTC_IN_MOD_2", "T3_IN_MOD"]
            t4 = register_map["DEB_DTC_IN_MOD_1", "T4_IN_MOD"]
            t5 = register_map["DEB_DTC_IN_MOD_1", "T5_IN_MOD"]
            t6 = register_map["DEB_DTC_IN_MOD_1", "T6_IN_MOD"]
            t7 = register_map["DEB_DTC_IN_MOD_1", "T7_IN_MOD"]

            self._app.log(f"{t0=}, {t1=}, {t2=}, {t3=}, {t4=}, {t5=}, {t6=}, {t7=}")

            self._app.post_message(DtcInModChanged(t0, t1, t2, t3, t4, t5, t6, t7))

        elif sync_id == MessageIdentifier.SYNC_HK_DATA:

            cmd, aeb_id, data, timestamp = data

            if cmd == 'command_deb_read_hk':
                hk_data = HousekeepingData("DEB", data, setup)
                deb_mode = f_fee_mode(hk_data["STATUS", "OPER_MOD"])
                self._app.log(f"DEB_MODE = {deb_mode.name}")
                self._app.post_message(DebModeChanged(deb_mode))
            elif cmd == 'command_aeb_read_hk':
                aeb_id = aeb_id[0]  # this comes from the args, so it's a list
                hk_data = HousekeepingData(aeb_id, data, setup)
                aeb_status = hk_data["STATUS", "AEB_STATUS"]
                self._app.log(f"AEB_STATE = {aeb_state(aeb_status).name}")

                # Power in handled by the DEB_DTC_AEB_ONOFF state from the DEB register map above.

                if aeb_status == aeb_state.OFF:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_onoff", False))
                elif aeb_status == aeb_state.INIT:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_init", True))
                elif aeb_status == aeb_state.POWER_UP:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_power_up", True))
                elif aeb_status == aeb_state.POWER_DOWN:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_power_down", True))
                elif aeb_status == aeb_state.CONFIG:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_config", True))
                elif aeb_status == aeb_state.IMAGE:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_image", True))
                elif aeb_status == aeb_state.PATTERN:
                    self._app.post_message(AebStateChanged(f"{aeb_id.lower()}_pattern", True))
