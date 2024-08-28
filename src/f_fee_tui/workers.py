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
from egse.fee.ffee import f_fee_mode
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.zmq import MessageIdentifier

from .messages import AebStateChanged
from .messages import DebModeChanged
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
                    self.handle_messages(sync_id, data)
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

    def handle_messages(self, sync_id, data):

        if sync_id == MessageIdentifier.F_FEE_REGISTER_MAP:
            register_map, _ = data
            register_map = RegisterMap("F-FEE", memory_map=register_map)

            deb_mode = f_fee_mode(register_map["DEB_DTC_FEE_MOD", "OPER_MOD"])

            if deb_mode != self.previous_deb_mode:
                self._app.post_message(DebModeChanged(deb_mode))
                self.previous_deb_mode = deb_mode

            # for aeb_id in "AEB1", "AEB2", "AEB3", "AEB4":
            for aeb_nr in (1, 2, 3, 4):
                aeb_state_type = f"aeb{aeb_nr}_onoff"
                aeb_state = register_map["DEB_DTC_AEB_ONOFF", f"AEB_IDX{aeb_nr}"]
                if aeb_state != self.previous_aeb_state.get(aeb_state_type, 0):
                    self._app.post_message(AebStateChanged(aeb_state_type, aeb_state))
                    self.previous_aeb_state[aeb_state_type] = aeb_state
